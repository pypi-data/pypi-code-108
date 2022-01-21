#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
__author__ = "socib ejerico team"
__copyright__ = "TODO copyright"
__credits__ = ["TODO credits"]
__license__ = "todo license"
__maintainer__ = "TODO maintainers"
__email__ = "maintainer at domain dot com"

"""
TODO doc
"""

import argparse
import sys
import os
import logging
import inspect
import profile

from datetime import timedelta
from timeit import default_timer as timer
from pathlib import Path

from filelock import Timeout, FileLock

from ejerico.bootstrap import Bootstrap
from ejerico.harvester import HarvesteringExecutor

def main():
    """ TODO doc """

    #[COMMAND] command line arguments (definition & parser) 
    parser = argparse.ArgumentParser("ejerico")

    parser.add_argument("-cp", "--config_path", type=str, help="configuration - config file path")
    # parser.add_argument("-cu", "--config_url", type=str, help="configuration - server url")
    # parser.add_argument("-cuu", "--config_username", type=str, help="configuration - server username")
    # parser.add_argument("-cup", "--config_password", type=str, help="configuration - server password")
    # parser.add_argument("-cut", "--config_token", type=str, help="configuration - server jwt token")


    args = parser.parse_args()

    harvest_start = timer()

    Path("{}{}.ejerico".format(str(Path.home()), os.sep)).mkdir(parents=True, exist_ok=True)

    harvest_pid_file = None
    harvest_lock_file = "{}{}.ejerico{}harvester.lock".format(str(Path.home()), os.sep, os.sep)
    harvest_lock = FileLock(harvest_lock_file)
    try:
        with harvest_lock.acquire(timeout=5):
            harvest_pid_file = open("{}{}.ejerico{}harvester.pid".format(str(Path.home()), os.sep, os.sep), 'w')
            harvest_pid_file.write(str(os.getpid()))
            harvest_pid_file.close()

            bootstrap = Bootstrap.instance()
            bootstrap.boot(args)
            
            executor = HarvesteringExecutor()
            if bootstrap.config.get("profile", default=False):
                path = "{}{}.ejerico{}{}.prof".format(str(Path.home()), os.sep, os.sep, bootstrap.config.get("profile_filename", default="ejerico"))
                profile.runctx("executor.run", globals(), locals(), filename=path)
            else:
                executor.run()

            os.remove("{}{}.ejerico{}harvester.pid".format(str(Path.home()), os.sep, os.sep))
    except Timeout:
        logging.warning("Another instance(PID: {}) of this application currently holds the lock.".format(os.getpid()))
    finally:
        harvest_end = timedelta(seconds=timer()-harvest_start)
        logging.info("[main] Harvesting process tooks {} to complete".format(harvest_end)) 

if __name__ == "__main__":
    main()
