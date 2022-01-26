from django.core.management.base import BaseCommand
from eveuniverse.models import EveSolarSystem, EveType


def get_input(text):
    """wrapped input to enable unit testing / patching"""
    return input(text)


class Command(BaseCommand):
    help = "Setup all needed data for buyback program to operate"

    def _update_models(self):

        self.stdout.write(
            "Adding %s objects to celery task queue. This may take a minute..."
            % (EveSolarSystem.__name__)
        )

        EveSolarSystem.objects.update_or_create_all_esi(
            include_children=False, wait_for_children=False
        )

        self.stdout.write(
            "Adding %s objects to celery task queue. This may take a few minutes..."
            % (EveType.__name__)
        )

        EveType.objects.update_or_create_all_esi(
            include_children=False,
            wait_for_children=False,
            enabled_sections=[
                EveType.Section.TYPE_MATERIALS,
                EveType.Section.MARKET_GROUPS,
            ],
        )

    def handle(self, *args, **options):
        self.stdout.write(
            "This command will load all the required data needed for the program to operate."
            "This process will take a very long time as we are loading every single items and solar system from ESI."
        )
        user_input = get_input("Are you sure you want to proceed? (y/N)?")
        if user_input.lower() == "y":
            self._update_models()
            self.stdout.write(
                "All objects added to celery queue. You can monitor the progress of these tasks from your AUTH dashboard. You can expect to see ~80k tasks added to the que. Once tasks are completed you can preload price data with buybackprogram_load_prices"
            )
        else:
            self.stdout.write("Aborted")
