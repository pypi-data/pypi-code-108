import logging

from django.core.management import BaseCommand
from django.db import connection

from isc_common.models.pg_class import Pg_class

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def handle(self, *args, **options):
        for sequence in Pg_class.objects.filter(relkind='S').order_by('relname'):
            with connection.cursor() as cursor:
                seq_name = sequence.relname
                table_name = seq_name[0:sequence.relname.rfind('_id_seq')]
                try:
                    cursor.execute("select max(id) + 1 from " + table_name)
                    row = cursor.fetchone()
                    id = row[0]

                    if isinstance(id, int):
                        cursor.execute(f'alter sequence {seq_name} restart with {id};')
                        # logger.info(f'seq: {table_name}, id: {id}')
                        print(f'seq: {table_name}, id: {id}')
                except Exception as e:
                    pass
                    # logger.error(e)
