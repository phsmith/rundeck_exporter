import json
import logging
import sys
import threading
from typing import NoReturn

import httpx
from cachetools import TTLCache, cached

from rundeck_exporter.args import rundeck_exporter_args as args
from rundeck_exporter.constants import RUNDECK_TOKEN, RUNDECK_USERPASSWORD

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Client for username/password auth — must persist cookies (JSESSIONID)
_user_client = httpx.Client(follow_redirects=True, verify=not args.rundeck_skip_ssl)
_auth_lock = threading.Lock()

# Client for token auth — thread-safe, connection pooling, no shared cookie state
_token_client = httpx.Client(follow_redirects=True, verify=not args.rundeck_skip_ssl)


def exit_with_msg(msg: str, level: str) -> NoReturn:
    """
    Logging wrapper method for logging and exiting
    """

    getattr(logging, level)(msg)
    sys.exit(1)


def request(endpoint: str) -> dict | list | None:
    """
    Method for managing requests on Rundeck API endpoints
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
                        )

        # Route /metrics/metrics based on configured auth method, not cookie presence.
        if endpoint == "/metrics/metrics" and args.rundeck_username and RUNDECK_USERPASSWORD:
            request_url = f"{args.rundeck_url}{endpoint}"
            response = _user_client.get(request_url, timeout=args.rundeck_requests_timeout)
            response_json = json.loads(response.text)
        else:
            request_url = f"{args.rundeck_url}/api/{args.rundeck_api_version}{endpoint}"
            response = _token_client.get(
                request_url,
                headers={"Accept": "application/json", "X-Rundeck-Auth-Token": RUNDECK_TOKEN or ""},
                timeout=args.rundeck_requests_timeout,
            )
            response_json = response.json()

        if response_json and isinstance(response_json, dict) and response_json.get("error") is True:
            raise Exception(response_json.get("message"))

        return response_json
    except json.JSONDecodeError as error:
        logging.critical(f"Invalid JSON Response from {request_url}. {error}")
    except Exception as error:
        logging.critical(response.text if response else str(error))
    return None


@cached(cache=TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl), lock=threading.Lock())
def cached_request(endpoint: str) -> dict | list | None:
    return request(endpoint)
