from django.core.cache import cache
from django.core.management.commands import migrate

from jnt_django_toolbox.context_managers.global_lock import (
    build_global_cache_key,
)
from jnt_django_toolbox.management.commands.migrate_concurrently import (
    MIGRATE_LOCK_NAME,
)


class Command(migrate.Command):
    """Reset cache lock for preventing parallel migrations."""

    def handle(self, *args, **options):  # noqa: WPS110
        """Command body."""
        cache.delete(build_global_cache_key(MIGRATE_LOCK_NAME))
        self.stdout.write(self.style.SUCCESS("Migrate lock was reseted"))
