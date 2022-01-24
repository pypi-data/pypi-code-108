import json
import logging

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from app_utils.logging import LoggerAddTag

from ... import __title__
from ...models import CharacterUpdateStatus

logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    help = "This command returns current statistics as JSON"

    def handle(self, *args, **options):
        stats = CharacterUpdateStatus.objects.statistics()
        stats_out = json.dumps(
            stats,
            sort_keys=True,
            indent=4,
            ensure_ascii=False,
            cls=DjangoJSONEncoder,
        )
        self.stdout.write(stats_out)
