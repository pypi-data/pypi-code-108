import logging

from django.core.management.base import BaseCommand
from esi.models import Token

from allianceauth.authentication.models import CharacterOwnership
from app_utils.logging import LoggerAddTag

from ... import __title__
from ...models import Character, Location, MailEntity
from ...tasks import update_all_characters
from . import get_input

logger = LoggerAddTag(logging.getLogger(__name__), __title__)


class Command(BaseCommand):
    help = "Reset all character data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reload",
            action="store_true",
            help="Also start reloading",
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Member Audit - Reset all characters")
        self.stdout.write("===================================")

        self.stdout.write(
            "This command deletes all locally stored character data, "
            "but maintains character skeletons, so they can be reloaded from ESI."
        )
        if options["reload"]:
            self.stdout.write("Will also start the task for reloading all characters.")

        self.stdout.write()
        self.stdout.write(
            "!! Please make sure your supervisors are shut down before running this command. !!"
        )
        self.stdout.write()
        self.stdout.write("ATTENTION!")
        self.stdout.write(
            "- ESI does not provide for historical data, "
            "so you will loose data like older mails and wallet journal entries. "
        )
        self.stdout.write(
            "- Also, all characters will be reset, e.g. sharing will be turned off."
        )
        self.stdout.write("- Doctrines will stay intact.")
        self.stdout.write()

        tokens = (
            Token.objects.all()
            .require_scopes(Character.get_esi_scopes())
            .require_valid()
        )
        character_ownerships = [
            obj
            for obj in CharacterOwnership.objects.filter(
                character__character_id__in=tokens.values_list(
                    "character_id", flat=True
                )
            )
            if (obj.user_id, obj.character.character_id)
            in tokens.values_list("user_id", "character_id")
        ]

        if not options["noinput"]:
            user_input = get_input(
                "Are you sure you want to proceed{}? (y/N)?".format(
                    f" for {len(character_ownerships)} character(s)"
                )
            )
        else:
            user_input = "y"
        if user_input.lower() == "y":
            logger.info("Running command reset_characters for %s characters.")
            self.stdout.write(
                self.style.SUCCESS("Character data reset has been started!")
            )
            self.stdout.write("Deleting Characters...")
            Character.objects.all().delete()
            self.stdout.write("Deleting Locations...")
            Location.objects.all().delete()
            self.stdout.write("Deleting MailEntities...")
            MailEntity.objects.all().delete()

            self.stdout.write(f"Recreating {len(character_ownerships)} characters ...")
            for character_ownership in character_ownerships:
                Character.objects.create(character_ownership=character_ownership)

            if options["reload"]:
                update_all_characters.delay()
                self.stdout.write("Started task to reload all character data")

            self.stdout.write(self.style.SUCCESS("Done"))
        else:
            self.stdout.write(self.style.WARNING("Aborted"))
