import json
import logging

import requests
from cachetools import TTLCache, cached

from rundeck_exporter.args import rundeck_exporter_args
from rundeck_exporter.constants import RUNDECK_TOKEN, RUNDECK_USERPASSWORD

args = rundeck_exporter_args.namespace

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Disable InsecureRequestWarning
requests.urllib3.disable_warnings()


def exit_with_msg(msg: str, level: str):
    """
    Logging wrapper method for logging and exiting
    """

    getattr(logging, level)(msg)
    exit(getattr(logging, level.upper()))


def request(endpoint: str) -> dict:
    """
    Method for managing requests on Rundeck API endpoints
    """

    response = None
    session = requests.Session()

    try:
        if args.rundeck_username and RUNDECK_USERPASSWORD:
            session.post(
                f"{args.rundeck_url}/j_security_check",
                data={"j_username": args.rundeck_username, "j_password": RUNDECK_USERPASSWORD},
                allow_redirects=True,
                verify=not args.rundeck_skip_ssl,
            )

        if endpoint == "/metrics/metrics" and session.cookies.get_dict().get("JSESSIONID"):
            request_url = f"{args.rundeck_url}{endpoint}"
            response = session.get(request_url, timeout=args.rundeck_requests_timeout)
            response_json = json.loads(response.text)
        else:
            request_url = f"{args.rundeck_url}/api/{args.rundeck_api_version}{endpoint}"
            response = session.get(
                request_url,
                headers={"Accept": "application/json", "X-Rundeck-Auth-Token": RUNDECK_TOKEN},
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


@cached(cache=TTLCache(maxsize=1024, ttl=args.rundeck_cached_requests_ttl))
def cached_request(endpoint: str) -> dict:
    return request(endpoint)
