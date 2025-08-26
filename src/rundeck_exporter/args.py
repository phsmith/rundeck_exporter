import textwrap

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from ast import literal_eval
from importlib.metadata import version
from os import getenv, cpu_count

from rundeck_exporter.constants import RUNDECK_DEFAULT_HOST, RUNDECK_DEFAULT_PORT


class RundeckExporterArgs:
    """Rundeck exporter command line arguments class."""

    parser = ArgumentParser(
        prog="rundeck_exporter",
        description=textwrap.dedent(
            """
        Rundeck Metrics Exporter

        required environment vars:
            RUNDECK_TOKEN\t Rundeck API Token
            RUNDECK_USERPASSWORD Rundeck User Password (Required when using RUNDECK_USERNAME or --rundeck.username)
        """
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        help="Enable debug mode",
        default=literal_eval(getenv("RUNDECK_EXPORTER_DEBUG", "False").capitalize()),
        action="store_true",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Shows rundeck_exporter current release version",
        action="version",
        version=f"%(prog)s v{version(__package__)}",
    )

    parser.add_argument(
        "--host",
        help=f"Host binding address. Default: {RUNDECK_DEFAULT_HOST}",
        metavar="RUNDECK_EXPORTER_HOST",
        default=getenv("RUNDECK_EXPORTER_HOST", RUNDECK_DEFAULT_HOST),
    )

    parser.add_argument(
        "--port",
        help=f"Host binding port. Default: {RUNDECK_DEFAULT_PORT}",
        metavar="RUNDECK_EXPORTER_PORT",
        type=int,
        default=getenv("RUNDECK_EXPORTER_PORT", RUNDECK_DEFAULT_PORT),
    )

    parser.add_argument(
        "--no_checks_in_passive_mode",
        dest="no_checks_in_passive_mode",
        help="The rundeck_exporter will not perform any checks while the Rundeck host is in passive execution mode",
        action="store_true",
        default=literal_eval(getenv("RUNDECK_EXPORTER_NO_CHECKS_IN_PASSIVE_MODE", "False").capitalize()),
    )

    parser.add_argument(
        "--threadpool_max_workers",
        help="The maximum number of workers in the threadpool to run rundeck_exporter asynchronous checks. Defaults to (number of CPUs) + 4",
        metavar="RUNDECK_EXPORTER_THREADPOOL_MAX_WORKERS",
        type=int,
        default=getenv("RUNDECK_EXPORTER_THREADPOOL_MAX_WORKERS", cpu_count() + 4),
    )

    parser.add_argument(
        "--rundeck.requests.timeout",
        dest="rundeck_requests_timeout",
        help="The maximum number of seconds that requests to the Rundeck API should timeout",
        metavar="RUNDECK_EXPORTER_REQUESTS_TIMEOUT",
        type=int,
        default=getenv("RUNDECK_EXPORTER_REQUESTS_TIMEOUT", 30),
    )

    parser.add_argument(
        "--rundeck.url",
        dest="rundeck_url",
        help="Rundeck Base URL [ REQUIRED ]",
        default=getenv("RUNDECK_URL"),
        metavar="RUNDECK_URL",
    )

    parser.add_argument(
        "--rundeck.skip_ssl",
        dest="rundeck_skip_ssl",
        help="Rundeck Skip SSL Cert Validate",
        default=literal_eval(getenv("RUNDECK_SKIP_SSL", "False").capitalize()),
        action="store_true",
    )

    parser.add_argument(
        "--rundeck.api.version",
        dest="rundeck_api_version",
        help="Defaults to 34",
        type=int,
        default=getenv("RUNDECK_API_VERSION", 34),
    )

    parser.add_argument(
        "--rundeck.username",
        dest="rundeck_username",
        help="Rundeck User with access to the system information",
        default=getenv("RUNDECK_USERNAME"),
        required=False,
    )

    parser.add_argument(
        "--rundeck.projects.executions",
        dest="rundeck_projects_executions",
        help="Get projects executions metrics",
        default=literal_eval(getenv("RUNDECK_PROJECTS_EXECUTIONS", "False").capitalize()),
        action="store_true",
    )

    parser.add_argument(
        "--rundeck.projects.executions.filter",
        dest="rundeck_project_executions_filter",
        help="""
                            Get the latest project executions filtered by time period
                            Can be in: [s]: seconds, [n]: minutes, [h]: hour, [d]: day, [w]: week, [m]: month, [y]: year
                            Defaults to 5n
                            """,
        default=getenv("RUNDECK_PROJECTS_EXECUTIONS_FILTER", "5n"),
    )

    parser.add_argument(
        "--rundeck.projects.executions.limit",
        dest="rundeck_projects_executions_limit",
        help="Project executions max results per query. Defaults to 20",
        type=int,
        default=getenv("RUNDECK_PROJECTS_EXECUTIONS_LIMIT", 20),
    )

    parser.add_argument(
        "--rundeck.projects.executions.cache",
        dest="rundeck_projects_executions_cache",
        help="Cache requests for project executions metrics query",
        default=literal_eval(getenv("RUNDECK_PROJECTS_EXECUTIONS_CACHE", "False").capitalize()),
        action="store_true",
    )

    parser.add_argument(
        "--rundeck.projects.filter",
        dest="rundeck_projects_filter",
        help="Get executions only from listed projects (delimiter = space)",
        default=getenv("RUNDECK_PROJECTS_FILTER", []),
        nargs="+",
        required=False,
    )

    parser.add_argument(
        "--rundeck.projects.nodes.info",
        dest="rundeck_projects_nodes_info",
        help="Display Rundeck projects nodes info metrics, currently only the `rundeck_project_nodes_total` metric is available. May cause high CPU load depending on the number of projects",
        action="store_true",
        default=literal_eval(getenv("RUNDECK_PROJECTS_NODES_INFO", "False").capitalize()),
    )

    parser.add_argument(
        "--rundeck.cached.requests.ttl",
        dest="rundeck_cached_requests_ttl",
        help="Rundeck cached requests expiration time. Defaults to 120",
        type=int,
        default=getenv("RUNDECK_CACHED_REQUESTS_TTL", 120),
    )

    parser.add_argument(
        "--rundeck.cpu.stats",
        dest="rundeck_cpu_stats",
        help="Show Rundeck CPU usage stats",
        action="store_true",
        default=literal_eval(getenv("RUNDECK_CPU_STATS", "False").capitalize()),
    )

    parser.add_argument(
        "--rundeck.memory.stats",
        dest="rundeck_memory_stats",
        help="Show Rundeck memory usage stats",
        action="store_true",
        default=literal_eval(getenv("RUNDECK_MEMORY_STATS", "False").capitalize()),
    )

    @property
    def namespace(self):
        return self.parser.parse_args()

    @property
    def empty_namespace(self):
        return self.parser.parse_args([])


rundeck_exporter_args = RundeckExporterArgs()
