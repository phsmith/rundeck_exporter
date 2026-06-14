import atexit
import logging
import re
import sys
import threading
from typing import NoReturn

import httpx
from cachetools import TTLCache
from prometheus_client import Counter

from rundeck_exporter.args import rundeck_exporter_args as args
from rundeck_exporter.constants import RUNDECK_TOKEN, RUNDECK_USERPASSWORD

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Client for username/password auth — must persist cookies (JSESSIONID)
_user_client = httpx.Client(follow_redirects=True, verify=not args.rundeck_skip_ssl)
_auth_lock = threading.Lock()

# Client for token auth — thread-safe, connection pooling, no shared cookie state
_token_client = httpx.Client(follow_redirects=True, verify=not args.rundeck_skip_ssl)

atexit.register(_user_client.close)
atexit.register(_token_client.close)

api_errors_total = Counter(
    "rundeck_exporter_api_errors_total",
    "Total number of Rundeck API request errors",
    ["endpoint"],
)

_cache = TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl)
_cache_lock = threading.Lock()


def _normalize_endpoint(endpoint: str) -> str:
    """
    Normalize a Rundeck API endpoint for consistent Prometheus metric labeling.
    
    Parameters:
    	endpoint (str): The API endpoint path, possibly containing query parameters and project identifiers.
    
    Returns:
    	str: The endpoint with query parameters removed and project paths normalized to `/project/{project}`.
    """
    endpoint = endpoint.split("?")[0]
    return re.sub(r"/project/[^/]+", "/project/{project}", endpoint)


def exit_with_msg(msg: str, level: str) -> NoReturn:
    """
    Log a message at the specified level and exit the process.
    
    Parameters:
        level (str): The logging level name (e.g., "critical", "error", "warning").
    """

    getattr(logging, level)(msg)
    sys.exit(1)


def request(endpoint: str) -> dict | list | None:
    """
    Fetches data from a Rundeck API endpoint.
    
    Returns:
        The parsed JSON response (dict or list) on success, None on failure.
    """

    response = None
    request_url = ""

    try:
        if args.rundeck_username and RUNDECK_USERPASSWORD:
            # Authenticate lazily with double-checked locking to avoid race conditions
            # when multiple ThreadPoolExecutor threads call request() simultaneously.
            if not _user_client.cookies.get("JSESSIONID"):
                with _auth_lock:
                    if not _user_client.cookies.get("JSESSIONID"):
                        _user_client.post(
                            f"{args.rundeck_url}/j_security_check",
                            data={"j_username": args.rundeck_username, "j_password": RUNDECK_USERPASSWORD},
                            timeout=args.rundeck_requests_timeout,
                        )
            # /metrics/metrics is an Actuator endpoint — no API version prefix when using session auth.
            # All other endpoints use the standard /api/{version} prefix.
            api_prefix = "" if endpoint == "/metrics/metrics" else f"/api/{args.rundeck_api_version}"
            request_url = f"{args.rundeck_url}{api_prefix}{endpoint}"
            response = _user_client.get(request_url, timeout=args.rundeck_requests_timeout)
        else:
            request_url = f"{args.rundeck_url}/api/{args.rundeck_api_version}{endpoint}"
            response = _token_client.get(
                request_url,
                headers={"Accept": "application/json", "X-Rundeck-Auth-Token": RUNDECK_TOKEN or ""},
                timeout=args.rundeck_requests_timeout,
            )

        response.raise_for_status()
        response_json = response.json()

        if response_json and isinstance(response_json, dict) and response_json.get("error") is True:
            raise ValueError(response_json.get("message"))

        return response_json
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError, ValueError) as error:
        if isinstance(error, httpx.HTTPStatusError):
            if error.response.status_code == 401 and args.rundeck_username and RUNDECK_USERPASSWORD:
                # Session expired — clear cookie so the next call triggers re-authentication
                with _auth_lock:
                    _user_client.cookies.clear()
            logging.critical(f"HTTP {error.response.status_code} from {request_url}: {error.response.text}")
        elif isinstance(error, httpx.TimeoutException):
            logging.critical(f"Request timed out for {request_url}: {error}")
        elif isinstance(error, httpx.RequestError):
            logging.critical(f"Request error for {request_url}: {error}")
        else:
            logging.critical(f"Rundeck API error from {request_url}: {error}")
        api_errors_total.labels(endpoint=_normalize_endpoint(endpoint)).inc()
    return None


def cached_request(endpoint: str) -> dict | list | None:
    """
    Retrieves a response from Rundeck, using cached results to avoid repeated requests.
    
    Parameters:
        endpoint (str): The Rundeck API endpoint path.
    
    Returns:
        dict | list | None: The parsed JSON response if successful, or None if the request failed.
    """
    with _cache_lock:
        if endpoint in _cache:
            return _cache[endpoint]
    result = request(endpoint)
    if result is not None:
        with _cache_lock:
            _cache[endpoint] = result
    return result
