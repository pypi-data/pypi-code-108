#!/usr/bin/python3
"""
Example code to scan Domintell and return list of installed modules.
"""

import asyncio
import time
import logging
import sys
import os, sys
from config import host
import domipy


def _on_message(message):
    print('received message', message)
    print(message)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
"""
please create a simple credentials.py:

host = {
    'ADDRESS': '192.168.0.1:17481',
    'USERNAME': '<your username>'
    'PASSWORD': '<your password>'
}

"""

#pylint: disable-msg=C0103
logging.info('Configuring controller for {}'.format(host['ADDRESS']))

controller = domipy.Controller(host['ADDRESS'])
controller.subscribe(_on_message)

logging.info('LOGIN')
controller.login(host['USERNAME'], host['PASSWORD'])

time.sleep(10)
logging.info('Starting scan')

controller.scan(None)

logging.info('Starting sleep')

input("Press enter to exit ")

logging.info('Exiting ...')
controller.stop()
