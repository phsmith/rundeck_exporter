#!/usr/bin/env python3
# encoding: utf-8

from rundeck_exporter.args import rundeck_exporter_args
from rundeck_exporter.constants import RUNDECK_TOKEN, RUNDECK_USERPASSWORD
from rundeck_exporter.metrics_collector import RundeckMetricsCollector
from rundeck_exporter.utils import exit_with_msg, logging


def main():
    try:
        args = rundeck_exporter_args.namespace

        if args.debug:
            logging.getLogger().setLevel("DEBUG")

        if not args.rundeck_url or not (RUNDECK_TOKEN or args.rundeck_username and RUNDECK_USERPASSWORD):
            exit_with_msg(
                msg="Rundeck URL and Token or User/Password are required.",
                level="critical",
            )

        metrics = RundeckMetricsCollector()
        metrics.run()
    except KeyboardInterrupt:
        logging.info("Rundeck exporter execution finished.")
    except Exception as error:
        raise (error)


if __name__ == "__main__":
    main()
