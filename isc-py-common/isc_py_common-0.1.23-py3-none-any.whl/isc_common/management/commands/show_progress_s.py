import logging

from django.conf import settings
from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from isc_common.ws.progressStack import ProgressSerialStack

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument('--mode', type=str)
    #     parser.add_argument('--qty', type=int)
    #     parser.add_argument('--id_user', type=int)

    def handle(self, *args, **options):
        user = User.objects.get(id=2)

        def func(progress):
            qty = 10
            print(user)
            for i in range(qty):
                progress.show(title=f'Тест {i}', label_contents=f'Text {i}', id=i)

            for i in range(qty):
                for j in range(qty + 1):
                    progress.setPercentsDone(percent=j * 10, id=i)

            for i in range(qty):
                progress.closed(id=i)

        ProgressSerialStack(
            func=func,
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{user.username}',
        )
