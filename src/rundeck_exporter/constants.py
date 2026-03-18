import os

RUNDECK_DEFAULT_HOST = "127.0.0.1"
RUNDECK_DEFAULT_PORT = 9620
RUNDECK_TOKEN: str | None = os.getenv("RUNDECK_TOKEN")
RUNDECK_USERPASSWORD: str | None = os.getenv("RUNDECK_USERPASSWORD")

RUNDECK_EXECUTION_STATUSES: tuple[str, ...] = ("succeeded", "running", "failed", "aborted", "unknown")
