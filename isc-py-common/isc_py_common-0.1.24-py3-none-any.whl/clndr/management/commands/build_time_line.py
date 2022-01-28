import logging

from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Создание модели календаря.'

    def add_arguments(self, parser):
        parser.add_argument('--calendar_id', type=int)
        parser.add_argument('--user_id', type=int)

    def handle(self, *args, **options):
        from clndr.time_line import Timeline

        calendar_id = options.get('calendar_id')
        user_id = options.get('user_id')

        logger.debug(self.help)

        data = dict(user_id=user_id)
        shiftsList = Timeline(calendar_id=calendar_id, logger=logger).build(data=data)
        shiftsList.write_2_file(f'dest_debug/calendar_{calendar_id}.js')
        json = shiftsList.to_json()
        print(len(json))
