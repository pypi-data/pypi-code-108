import logging

from django.conf import settings
from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from isc_common.ws.progressStack import ProgressStack

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str)
        parser.add_argument('--qty', type=int)
        parser.add_argument('--id_user', type=int)
        parser.add_argument('--cancel', type=bool)

    def handle(self, *args, **options):
        mode = options.get('mode')
        qty = options.get('qty')
        id_user = options.get('id_user')
        cancel = options.get('cancel', False)

        user = User.objects.get(id=id_user)

        progress = ProgressStack(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{user.username}',
            props=1 if cancel else 0,
            user_id=user.id
        )

        if mode == 'open':
            for i in range(qty):
                progress.show(title=f'Тест {i}', label_contents=f'Text {i}', id=i)

            for i in range(qty):
                for j in range(11):
                    progress.setPercentsDone(percent=j * 10, id=i)

            # sleep(3)
            # for i in range(qty):
            #     progress.close(id=i)
