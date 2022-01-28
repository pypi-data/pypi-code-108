import datetime
import logging

from django.core.management import BaseCommand
from django.db import connections, connection, transaction

from history.models.history import History

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        with connections['history'].cursor() as cursor:
            begdate = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            begdate = begdate.replace(day=begdate.day - 1, hour=0, minute=0, second=0, microsecond=0)
            enddate = begdate.replace(day=begdate.day + 1)
            cursor.execute('''select
                                    username,
                                    fio,
                                    count(*)
                                from history_history
                                where date between %s and %s
                                group by username, fio
                                order by fio ''', [begdate, enddate])
            count_blocks = cursor.fetchall()
            res = [dict(username=count_block[0], fio=count_block[1], count=count_block[2]) for count_block in count_blocks]
            for r in res:
                print(r)

        print('Aggregate done.')
