import logging

from django.core.management import BaseCommand

logger = logging.getLogger(__name__)

import logging
import tqdm


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.addHandler(TqdmLoggingHandler())
        for i in tqdm.tqdm(range(100)):
            logger.info(i)
