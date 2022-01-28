import logging

from django.core.management import BaseCommand

import code_generator

logger = logging.getLogger(__name__)
appModel = None


class Command(BaseCommand):
    help = "Создание приложения."

    def handle(self, *args, **options):
        try:
            logger.debug(self.help)

            model = code_generator.appModel()
            model.write_entity()

            logger.debug(f'{self.help}, завершено.')
        except Exception as ex:
            raise ex
