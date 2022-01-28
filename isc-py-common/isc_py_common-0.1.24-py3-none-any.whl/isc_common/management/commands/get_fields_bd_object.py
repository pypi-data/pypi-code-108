import logging

from django.core.management import BaseCommand
from django.db import connection

from code_generator.core.writer import dbl_qutes_str
from isc_common.common.mat_views import exists_table

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--obj_name', type=str)
        parser.add_argument('--prefix', type=str)

    def handle(self, *args, **options):
        # obj_name = options.get('obj_name')
        # prefix = options.get('prefix', None)
        #
        # sql_text = '''SELECT a.attname
        #                 --        pg_catalog.format_type(a.atttypid, a.atttypmod),
        #                 --        a.attnotnull,
        #                 --        a.atthasdef,
        #                 --        a.attnum
        #                 FROM pg_catalog.pg_attribute a
        #                 WHERE a.attrelid = (
        #                     SELECT c.oid
        #                     FROM pg_catalog.pg_class c --Этот подзапрос возвращает --идентификатор таблицы...
        #                              LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        #                     WHERE pg_catalog.pg_table_is_visible(c.oid)
        #                       AND c.relname ~ %s
        #                 )
        #                   AND a.attnum > 0
        #                   AND NOT a.attisdropped
        #                 ORDER BY a.attnum
        #                 '''
        #
        # sql_text = '''SELECT 1
        #                 FROM   pg_catalog.pg_class c
        #                 JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        #                 WHERE  n.nspname = 'schema_name'
        #                 AND    c.relname = 'table_name'
        #                 AND    c.relkind = 'r'''
        #
        # with connection.cursor() as cursor:
        #     cursor.execute(sql_text, [obj_name])
        #     rows = cursor.fetchall()
        #     columns = []
        #     for row in rows:
        #         column_name, = row
        #         if prefix:
        #             columns.append(f'{prefix}.{dbl_qutes_str(column_name)}')
        #         else:
        #             columns.append(dbl_qutes_str(column_name))
        #
        # res = ',\n'.join(columns)
        print(exists_table('ckk_material_askon_mview'))
