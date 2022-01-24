import logging

from django.core.management.base import BaseCommand

from app_utils.logging import LoggerAddTag

from ... import __title__
from ...models import Character
from ...tasks import update_all_characters
from . import get_input

logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    help = "Updates all characters from ESI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Forced update also updates non-stale data",
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Member Audit - Update all characters")
        self.stdout.write("=====================================")

        self.stdout.write(
            "Forced update: {}".format("yes" if options["force"] else "no")
        )

        character_count = Character.objects.count()
        if character_count > 0:
            if not options["noinput"]:
                user_input = get_input(
                    f"Are you sure you want to proceed for {character_count} "
                    "character(s)? (y/N)?"
                )
            else:
                user_input = "y"

            if user_input.lower() == "y":
                logger.info(
                    "Running command update_all_characters for %s characters.",
                    character_count,
                )
                self.stdout.write("Starting task to update all characters...")
                update_all_characters.delay(force_update=options["force"])
                self.stdout.write(self.style.SUCCESS("Done"))

        else:
            self.stdout.write(self.style.WARNING("No characters found"))
