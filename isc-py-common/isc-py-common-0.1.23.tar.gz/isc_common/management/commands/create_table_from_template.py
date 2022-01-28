import logging

from django.core.management import BaseCommand
from django.db import connection

from isc_common.common.mat_views import create_table

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--tablename', type=str)

    def handle(self, *args, **options):
        tablename = options.get('tablename')

        create_table(
            sql_str=f'''select * from {tablename}_view''',
            table_name=f'''{tablename}_tbl''',
            primary_key=['id', 'location_id']
        )
