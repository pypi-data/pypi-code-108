#!/usr/bin/env python
"""
This is a working literal translation of the jq based moby-download frozen
image tool.


Could be done far smaller.

"""

import os
import signal
import sys
import time

from devapp.app import flag, run_app

flag.string('dir', './images', 'Exisiting target dir', short_name='d')
flag.string('repo', 'busybox:latest', 'repo')


def cleanup(*args):
    print('Exiting')
    os.system('touch /root/foooo')
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def main():
    for i in range(1, 100):
        print('stasring')
    while True:
        time.sleep(60)


run = lambda: run_app(main)

if __name__ == '__main__':
    run()
