import json
import logging
import sys
import threading
from typing import NoReturn

import requests
import urllib3
from cachetools import TTLCache, cached

from rundeck_exporter.args import rundeck_exporter_args
from rundeck_exporter.constants import RUNDECK_TOKEN, RUNDECK_USERPASSWORD

args = rundeck_exporter_args.namespace

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Suppress only insecure-request warnings when SSL verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Module-level session reused across all requests for connection pooling
_session = requests.Session()
_auth_lock = threading.Lock()


def exit_with_msg(msg: str, level: str) -> NoReturn:
    """
    Logging wrapper method for logging and exiting
    """

    getattr(logging, level)(msg)
    sys.exit(1)


def request(endpoint: str) -> dict | None:
    """
    Method for managing requests on Rundeck API endpoints
    """

    response = None
    request_url = ""

    try:
        if args.rundeck_username and RUNDECK_USERPASSWORD:
            # Authenticate lazily with double-checked locking to avoid race conditions
            # when multiple ThreadPoolExecutor threads call request() simultaneously.
            if not _session.cookies.get_dict().get("JSESSIONID"):
                with _auth_lock:
                    if not _session.cookies.get_dict().get("JSESSIONID"):
                        _session.post(
                            f"{args.rundeck_url}/j_security_check",
                            data={"j_username": args.rundeck_username, "j_password": RUNDECK_USERPASSWORD},
                            allow_redirects=True,
                            verify=not args.rundeck_skip_ssl,
                        )

        # Route /metrics/metrics based on configured auth method, not cookie presence.
        # With a shared session, Rundeck may set a JSESSIONID even during token-based
        # requests, so checking cookies is not a reliable proxy for "session auth is active".
        if endpoint == "/metrics/metrics" and args.rundeck_username and RUNDECK_USERPASSWORD:
            request_url = f"{args.rundeck_url}{endpoint}"
            response = _session.get(
                request_url, verify=not args.rundeck_skip_ssl, timeout=args.rundeck_requests_timeout
            )
            response_json = json.loads(response.text)
        else:
            request_url = f"{args.rundeck_url}/api/{args.rundeck_api_version}{endpoint}"
            response = _session.get(
                request_url,
                headers={"Accept": "application/json", "X-Rundeck-Auth-Token": RUNDECK_TOKEN or ""},
                verify=not args.rundeck_skip_ssl,
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


@cached(cache=TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl))
def cached_request(endpoint: str) -> dict | None:
    return request(endpoint)
