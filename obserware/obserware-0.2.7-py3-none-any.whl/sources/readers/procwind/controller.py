"""
Obserware
Copyright (C) 2021 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import logging

import psutil

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
    datefmt="[%H:%M:%S] [%d %b %Y]",
)


def log_process_interaction(logecode, prociden, taskverb):
    if logecode == 0:
        logging.warning("PID %d was %s successfully" % (prociden, taskverb))
    elif logecode == 1:
        logging.warning(
            "PID %d could not be %s as it does not exist" % (prociden, taskverb)
        )
    elif logecode == 2:
        logging.warning(
            "PID %d could not be %s due to improper privileges" % (prociden, taskverb)
        )


def kill_process(prociden):
    taskverb = "killed"
    try:
        psutil.Process(prociden).kill()
        log_process_interaction(0, prociden, taskverb)
    except psutil.NoSuchProcess:
        log_process_interaction(1, prociden, taskverb)
    except psutil.AccessDenied:
        log_process_interaction(2, prociden, taskverb)


def terminate_process(prociden):
    taskverb = "terminated"
    try:
        psutil.Process(prociden).terminate()
        log_process_interaction(0, prociden, taskverb)
    except psutil.NoSuchProcess:
        log_process_interaction(1, prociden, taskverb)
    except psutil.AccessDenied:
        log_process_interaction(2, prociden, taskverb)


def resume_process(prociden):
    taskverb = "resumed"
    try:
        psutil.Process(prociden).resume()
        log_process_interaction(0, prociden, taskverb)
    except psutil.NoSuchProcess:
        log_process_interaction(1, prociden, taskverb)
    except psutil.AccessDenied:
        log_process_interaction(2, prociden, taskverb)


def suspend_process(prociden):
    taskverb = "suspended"
    try:
        psutil.Process(prociden).suspend()
        log_process_interaction(0, prociden, taskverb)
    except psutil.NoSuchProcess:
        log_process_interaction(1, prociden, taskverb)
    except psutil.AccessDenied:
        log_process_interaction(2, prociden, taskverb)
