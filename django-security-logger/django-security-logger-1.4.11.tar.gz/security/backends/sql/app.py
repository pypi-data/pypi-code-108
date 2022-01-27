from django.db.models.signals import pre_migrate, post_migrate

from security.backends.app import SecurityBackend

from . import db_helpers


def start_migration(sender, **kwargs):
    db_helpers.is_running_migration = True


def end_migration(sender, **kwargs):
    db_helpers.is_running_migration = False


class SecuritySQLBackend(SecurityBackend):

    name = 'security.backends.sql'
    label = 'security_backends_sql'
    backend_name = 'sql'
    writer = 'security.backends.sql.writer.SQLBackendWriter'
    reader = 'security.backends.sql.reader.SQLBackendReader'

    def ready(self):
        super().ready()
        pre_migrate.connect(start_migration, sender=self)
        post_migrate.connect(end_migration, sender=self)
