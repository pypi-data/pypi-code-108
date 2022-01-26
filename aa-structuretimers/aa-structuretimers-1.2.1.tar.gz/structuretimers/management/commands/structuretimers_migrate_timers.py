from django.core.management.base import BaseCommand
from django.db import models
from django.utils.timezone import now
from eveuniverse.models import EveSolarSystem

from app_utils.django import app_labels

from ...models import Timer


def get_input(text):
    """wrapped input to enable unit testing / patching"""
    return input(text)


# objectives
OBJECTIVE_CHOICES = [
    (Timer.Objective.HOSTILE, "Hostile"),
    (Timer.Objective.FRIENDLY, "Friendly"),
    (Timer.Objective.NEUTRAL, "Neutral"),
    (Timer.Objective.UNDEFINED, "Undefined"),
]

# structure types
STRUCTURE_TYPE_POCO = 2233
STRUCTURE_TYPE_I_HUB = 2233
STRUCTURE_TYPE_TCU = 32226
STRUCTURE_TYPE_POS_S = 20062
STRUCTURE_TYPE_POS_M = 20061
STRUCTURE_TYPE_POS_L = 16213
STRUCTURE_TYPE_ASTRAHUS = 35832
STRUCTURE_TYPE_FORTIZAR = 35833
STRUCTURE_TYPE_KEEPSTAR = 35834
STRUCTURE_TYPE_RAITARU = 35825
STRUCTURE_TYPE_AZBEL = 35826
STRUCTURE_TYPE_SOTIYO = 35827
STRUCTURE_TYPE_ATHANOR = 35835
STRUCTURE_TYPE_TATARA = 35836
STRUCTURE_TYPE_PHAROLUX = 35840
STRUCTURE_TYPE_TENEBREX = 37534
STRUCTURE_TYPE_ANSIBLEX = 35841
STRUCTURE_TYPE_STATION = 1529

STRUCTURE_CHOICES = [
    (STRUCTURE_TYPE_POCO, "POCO"),
    (STRUCTURE_TYPE_I_HUB, "I-HUB"),
    (STRUCTURE_TYPE_TCU, "TCU"),
    (STRUCTURE_TYPE_POS_S, "POS[S]"),
    (STRUCTURE_TYPE_POS_M, "POS[M]"),
    (STRUCTURE_TYPE_POS_L, "POS[L]"),
    (STRUCTURE_TYPE_ASTRAHUS, "Astrahus"),
    (STRUCTURE_TYPE_FORTIZAR, "Fortizar"),
    (STRUCTURE_TYPE_KEEPSTAR, "Keepstar"),
    (STRUCTURE_TYPE_RAITARU, "Raitaru"),
    (STRUCTURE_TYPE_AZBEL, "Azbel"),
    (STRUCTURE_TYPE_SOTIYO, "Sotiyo"),
    (STRUCTURE_TYPE_ATHANOR, "Athanor"),
    (STRUCTURE_TYPE_TATARA, "Tatara"),
    (STRUCTURE_TYPE_PHAROLUX, "Pharolux Cyno Beacon"),
    (STRUCTURE_TYPE_TENEBREX, "Tenebrex Cyno Jammer"),
    (STRUCTURE_TYPE_ANSIBLEX, "Ansiblex Jump Gate"),
    (STRUCTURE_TYPE_ATHANOR, "Moon Mining Cycle"),
]


class Command(BaseCommand):
    help = (
        "Removes all app-related data from the database. "
        "Run this command before zero migrations, "
        "which would otherwise fail due to FK constraints."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--test",
            action="store_true",
            help="Perform's a test run. Does not actually migrate, but will show potential issues.",
        )

    def _migrate_timers(
        self, auth_timers_qs: models.QuerySet, is_test: bool = False
    ) -> None:
        objective_map = {x[1]: x[0] for x in OBJECTIVE_CHOICES}
        structure_map = {x[1]: x[0] for x in STRUCTURE_CHOICES}
        migrated_count = 0
        skipped_count = 0
        for auth_timer in auth_timers_qs:
            try:
                eve_solar_system = EveSolarSystem.objects.get(name=auth_timer.system)
            except EveSolarSystem.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Can not migrate timer '{auth_timer}', "
                        f"due to invalid solar system: {auth_timer.system}"
                    )
                )
                skipped_count += 1
                continue

            if auth_timer.structure in structure_map:
                structure_type_id = structure_map[auth_timer.structure]
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Can not migrate timer '{auth_timer}', "
                        f"due to invalid structure type: {auth_timer.structure}"
                    )
                )
                skipped_count += 1
                continue

            if auth_timer.objective in objective_map:
                objective = objective_map[auth_timer.objective]
            else:
                objective = Timer.Objective.UNDEFINED

            if auth_timer.corp_timer:
                visibility = Timer.Visibility.CORPORATION
            else:
                visibility = Timer.Visibility.UNRESTRICTED

            details_lower = auth_timer.details.lower()
            if "Moon Mining Cycle" in auth_timer.structure:
                timer_type = Timer.Type.MOONMINING
            elif "armor" in details_lower:
                timer_type = Timer.Type.ARMOR
            elif "hull" in details_lower:
                timer_type = Timer.Type.HULL
            elif "final" in details_lower:
                timer_type = Timer.Type.FINAL
            elif "unanchor" in details_lower:
                timer_type = Timer.Type.UNANCHORING
            elif "anchor" in details_lower:
                timer_type = Timer.Type.ANCHORING
            else:
                timer_type = Timer.Type.NONE

            if not is_test:
                try:
                    Timer.objects.get(
                        eve_solar_system=eve_solar_system,
                        structure_type_id=structure_type_id,
                        date=auth_timer.eve_time,
                        details_notes=auth_timer.details,
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping timer '{auth_timer}', since it already exists"
                        )
                    )
                    skipped_count += 1

                except Timer.DoesNotExist:
                    Timer.objects.create(
                        eve_solar_system=eve_solar_system,
                        structure_type_id=structure_type_id,
                        date=auth_timer.eve_time,
                        user=auth_timer.user,
                        location_details=auth_timer.planet_moon,
                        timer_type=timer_type,
                        details_notes=auth_timer.details,
                        objective=objective,
                        is_important=auth_timer.important,
                        visibility=visibility,
                        eve_character=auth_timer.eve_character,
                        eve_corporation=auth_timer.eve_corp,
                        eve_alliance=auth_timer.eve_corp.alliance,
                    )
                    migrated_count += 1

        self.stdout.write(
            f"Results: Migrated: {migrated_count} - Skipped: {skipped_count} "
            f"- Total: {auth_timers_qs.count()}"
        )

    def handle(self, *args, **options):
        if "timerboard" not in app_labels():
            self.stdout.write(
                self.style.WARNING(
                    "The timerboard app from Auth is not installed. Aborted."
                )
            )
        else:
            from allianceauth.timerboard.models import Timer as AuthTimer

            auth_timers_qs = AuthTimer.objects.filter(eve_time__gt=now())
            self.stdout.write(
                f"This command will migrate {auth_timers_qs.count()} "
                "pending timers from the "
                "Auth's timerboard app to this app. "
            )
            self.stdout.write(
                "Note that timers that have been migrated previously "
                "will not be migrated again "
                "unless the migrated timers have been changed significantly."
            )
            is_test = options["test"]
            if is_test:
                self.stdout.write("Test run - will not migrate")

            user_input = get_input("Are you sure you want to proceed? (y/N)?")
            if user_input.lower() == "y":
                self.stdout.write("Starting migrating timers. Please stand by.")
                self._migrate_timers(auth_timers_qs, is_test=is_test)
                self.stdout.write(self.style.SUCCESS("Migration complete!"))
            else:
                self.stdout.write(self.style.WARNING("Aborted."))
