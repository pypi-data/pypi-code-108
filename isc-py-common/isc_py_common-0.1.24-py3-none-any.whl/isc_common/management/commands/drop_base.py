import logging

from django.core.management import BaseCommand
from django.db import connections

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str)
        parser.add_argument('--connection', type=str)

    def handle(self, *args, **options):
        if options['name']:
            self.name = options['name']
        else:
            raise Exception(f'name param not exists')

        if options['connection']:
            self.connection = options['connection']
        else:
            raise Exception(f'connection param not exists')

        with connections[self.connection].cursor() as cursor:
            try:
                cursor.execute(f'DROP DATABASE IF EXISTS {self.name}')

            except Exception as e:
                logger.error(e)
