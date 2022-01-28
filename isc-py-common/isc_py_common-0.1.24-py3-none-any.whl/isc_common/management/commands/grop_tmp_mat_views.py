import logging

from django.core.management import BaseCommand
from django.db import connection

from isc_common.models.mat_view import Mat_view

logger = logging.getLogger(__name__)


def grop_mat_views(relname=None, schemaname=None, loger_func=lambda str: print(str), prefix='tmp'):
    def dbl_qutes_str(str):
        return f'"{str}"'

    # loger_func('start: grop_tmp_mat_views')

    if relname and schemaname:
        query = Mat_view.objects.filter(relname=relname, schemaname=schemaname)
    elif relname and not schemaname:
        query = Mat_view.objects.filter(relname=relname)
    elif not relname and schemaname:
        query = Mat_view.objects.filter(schemaname=schemaname)
    else:
        query = Mat_view.objects.filter()

    for mat_view in query:
        try:
            with connection.cursor() as cursor:
                # logger.debug(f'Creating: {m_view_name}')
                if mat_view.relname.find(f'{prefix}_') != -1:
                    loger_func(f'Droping: {dbl_qutes_str(mat_view.relname)}')
                    cursor.execute(f'DROP MATERIALIZED VIEW {dbl_qutes_str(mat_view.relname)} CASCADE;')
                    loger_func(f'Droped.')
                    # print(f'Function created')
        except Exception as ex:
            raise ex

    loger_func('Cleaned Temp matViews')

class Command(BaseCommand):

    def handle(self, *args, **options):
        grop_mat_views()
