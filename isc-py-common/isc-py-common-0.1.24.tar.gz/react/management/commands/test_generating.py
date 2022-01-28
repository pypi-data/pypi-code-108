import logging

from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from react.models.generators import TypeScriptGenerator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        TypeScriptGenerator().generate(data={'pages_ids': [3], 'httpHeaders': {'USER_ID': 7}}, user=User.objects.get(id=7))
        # print(TypeScriptGenerator()._get_text('Фоновый рисунок для всего приложения'))
        print("Done.")
