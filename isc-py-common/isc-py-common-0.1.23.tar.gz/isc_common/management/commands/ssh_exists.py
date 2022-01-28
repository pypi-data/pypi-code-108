import logging
import os
from os import walk
from pathlib import Path

from django.core.management import BaseCommand
from isc_common.ssh.ssh_client import SSH_Client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        # parser.add_argument('--message', type=str)

    def handle(self, *args, **options):
        SSH_HOST = '192.168.0.158'
        SSH_PORT = 22
        SSH_USER = 'download-image-content'
        SSH_PASSWORD = 'download-image-content'

        c_dumps_path = '/home/download-image-content/images/FILES'
        c_dumps_path = '/home/download-image-content/images'


        SSH_CLIENT = SSH_Client(hostname=SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, port=SSH_PORT)
        res = SSH_CLIENT.exists(f'{c_dumps_path}/.git')
        print(res)
