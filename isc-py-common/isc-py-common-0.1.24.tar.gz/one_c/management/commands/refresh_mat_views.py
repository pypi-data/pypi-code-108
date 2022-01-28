import configparser
import logging
from tkinter import *

from django.core.management import BaseCommand
from django.db import connection

from one_c.models.entity_1c import Entity_1c
from one_c.models.mat_view import Mat_view
from one_c.models.one_c_params_entity_view import One_c_params_entity_view

logger = logging.getLogger(__name__)


class ExceptionOnDocLoading(Exception):
    pass


class Command(BaseCommand):
    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def handle(self, *args, **options):
        try:
            for mat_view in Mat_view.objects.filter():
                with connection.cursor() as cursor:
                    # logger.debug(f'Creating: {m_view_name}')
                    print(f'Refreshing: {self.dbl_qutes_str(mat_view.relname)}')
                    cursor.execute(f'REFRESH MATERIALIZED VIEW {self.dbl_qutes_str(mat_view.relname)};')
                    print(f'Refreshed')
                    # cursor.execute(f'CREATE OR REPLACE FUNCTION tg_refresh_{mat_view.relname}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN REFRESH MATERIALIZED VIEW {mat_view.relname}; RETURN NULL; END; $$;')
                    # logger.debug(f'Created')
                    # print(f'Function created')

        except ExceptionOnDocLoading as ex:
            self.root.withdraw()
            logger.error('\n !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')

            for msg_item in ex.args:
                logger.error(msg_item)

            logger.error('\n !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
