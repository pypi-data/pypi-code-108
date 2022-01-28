import logging

from django.core.management import BaseCommand

from isc_common.common.mat_views import create_insert_update_delete_function_of_table

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--tablename', type=str)

    def handle(self, *args, **options):
        tablename = options.get('tablename')

        create_insert_update_delete_function_of_table(table_name=tablename)
