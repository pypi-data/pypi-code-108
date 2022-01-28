import logging

from django.core.management import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--filename', type=str)

    def handle(self, *args, **options):
        filename = options.get('filename')
        file = open(filename)

        with connection.cursor() as cursor:
            try:
                for sql_line in file.readline():
                    cursor.execute(sql_line)

            except Exception as e:
                logger.error(e)
