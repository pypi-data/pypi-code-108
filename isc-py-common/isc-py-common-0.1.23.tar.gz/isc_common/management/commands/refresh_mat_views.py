import logging

from django.core.management import BaseCommand
from django.db import connection

from isc_common.models.mat_view import Mat_view

logger = logging.getLogger(__name__)


def refresh_mat_view(relname=None, schemaname=None, loger_func=lambda str: print(str)):
    def dbl_qutes_str(str):
        return f'"{str}"'

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
                loger_func(f'Refreshing: {dbl_qutes_str(mat_view.relname)}')
                cursor.execute(f'REFRESH MATERIALIZED VIEW{dbl_qutes_str(mat_view.relname)};')
                loger_func(f'Refreshed')
                # cursor.execute(f'CREATE OR REPLACE FUNCTION tg_refresh_{mat_view.relname}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN REFRESH MATERIALIZED VIEW {mat_view.relname}; RETURN NULL; END; $$;')
                # logger.debug(f'Created')
                # print(f'Function created')
        except Exception as ex:
            raise ex


class Command(BaseCommand):

    def handle(self, *args, **options):
        refresh_mat_view()
