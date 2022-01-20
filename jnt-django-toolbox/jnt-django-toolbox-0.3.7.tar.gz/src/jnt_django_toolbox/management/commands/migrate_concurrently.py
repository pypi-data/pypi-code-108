from django.core.management.commands import migrate

from jnt_django_toolbox.context_managers import global_lock

MIGRATE_LOCK_NAME = "db_migrate"


class Command(migrate.Command):
    """
    Migrate concurrently.

    Only 1 migrate will be runned at once.
    """

    def handle(self, *args, **options):  # noqa: WPS110
        """Command body."""
        with global_lock(MIGRATE_LOCK_NAME) as acquired:
            if acquired:
                super().handle(*args, **options)
            else:
                self.stdout.write(
                    self.style.WARNING("Migration already runned"),
                )
