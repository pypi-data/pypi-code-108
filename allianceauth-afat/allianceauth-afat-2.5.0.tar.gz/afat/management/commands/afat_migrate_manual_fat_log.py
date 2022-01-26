"""
Migrate the old manual FAT log into the new log table
"""

# Django
from django.core.management.base import BaseCommand

# Alliance Auth AFAT
from afat.models import AFatLog, AFatLogEvent, ManualAFat


def get_input(text) -> str:
    """
    Wrapped input to enable import
    :param text:
    :type text:
    :return:
    :rtype:
    """

    return input(text)


class Command(BaseCommand):
    """
    Migrate manual FAT log
    """

    help = "Migrating the old Manual FAT log into the new log table"

    def _migrate_manual_fat_log(self) -> None:
        """
        Start the migration
        :return:
        :rtype:
        """

        manual_fat_logs = ManualAFat.objects.all()

        if manual_fat_logs.count() > 0:
            for manual_log in manual_fat_logs:
                if manual_log.created_at is not None:
                    afat_log = AFatLog()

                    afat_log.user_id = manual_log.creator_id
                    afat_log.log_time = manual_log.created_at
                    afat_log.log_event = AFatLogEvent.MANUAL_FAT
                    afat_log.log_text = (
                        f"Pilot {manual_log.character} manually added. "
                        f"(Migrated from old Manual FAT log)"
                    )
                    afat_log.fatlink_hash = manual_log.afatlink.hash
                    afat_log.save()

                manual_log.delete()

        self.stdout.write(self.style.SUCCESS("Migration complete!"))

    def handle(self, *args, **options):
        """
        Ask before running ...
        :param args:
        :type args:
        :param options:
        :type options:
        :return:
        :rtype:
        """

        self.stdout.write(
            "This will migrate the old Manual FAT log into the new log table. "
            "Migrated entires will be removed from the old Manual FAT log to "
            "prevent duplicates."
        )

        user_input = get_input("Are you sure you want to proceed? (yes/no)?")

        if user_input == "yes":
            self.stdout.write("Starting import. Please stand by.")
            self._migrate_manual_fat_log()
        else:
            self.stdout.write(self.style.WARNING("Aborted."))
