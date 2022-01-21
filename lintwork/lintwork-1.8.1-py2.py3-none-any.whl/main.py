# -*- coding: utf-8 -*-

import sys

from lintwork.cmd.argument import Argument
from lintwork.cmd.banner import BANNER
from lintwork.config.config import Config, ConfigException
from lintwork.lint.lint import Lint, LintException
from lintwork.logger.logger import Logger
from lintwork.queue.queue import Queue, QueueException
from lintwork.work.work import Work, WorkException


def main():
    print(BANNER)

    argument = Argument()
    arg = argument.parse(sys.argv)

    try:
        config = Config()
        config.config_file = arg.config_file
        config.lint_project = arg.lint_project
        config.listen_url = arg.listen_url
        config.output_file = arg.output_file
    except ConfigException as e:
        Logger.error(str(e))
        return -1

    try:
        work = Work(config)
    except WorkException as e:
        Logger.error(str(e))
        return -2

    Logger.info("lint running")

    if len(config.listen_url) != 0:
        try:
            lint = Lint(config)
            lint.run(work.routine)
        except LintException as e:
            Logger.error(str(e))
            return -3
    else:
        try:
            queue = Queue(config)
            queue.run(work.routine, config.lint_project)
        except QueueException as e:
            Logger.error(str(e))
            return -4

    Logger.info("lint exiting")

    return 0
