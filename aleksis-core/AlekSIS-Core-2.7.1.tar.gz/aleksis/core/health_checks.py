from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext as _

from dbbackup import utils as dbbackup_utils
from dbbackup.storage import get_storage
from django_celery_results.models import TaskResult
from health_check.backends import BaseHealthCheckBackend

from aleksis.core.models import DataCheckResult


class DataChecksHealthCheckBackend(BaseHealthCheckBackend):
    """Checks whether there are unresolved data problems."""

    critical_service = False

    def check_status(self):
        if DataCheckResult.objects.filter(solved=False).exists():
            self.add_error(_("There are unresolved data problems."))

    def identifier(self):
        return self.__class__.__name__


class BaseBackupHealthCheck(BaseHealthCheckBackend):
    """Common base class for backup age checks."""

    critical_service = False
    content_type = None
    configured_seconds = None

    def check_status(self):
        storage = get_storage()

        try:
            backups = storage.list_backups(content_type=self.content_type)
        except Exception as ex:
            self.add_error(_("Error accessing backup storage: {}").format(str(ex)))
            return

        if backups:
            last_backup = backups[:1]
            last_backup_time = dbbackup_utils.filename_to_date(last_backup[0])
            time_gone_since_backup = datetime.now() - last_backup_time

            # Check if backup is older than configured time
            if time_gone_since_backup.seconds > self.configured_seconds:
                self.add_error(_("Last backup {}!").format(time_gone_since_backup))
        else:
            self.add_error(_("No backup found!"))


class DbBackupAgeHealthCheck(BaseBackupHealthCheck):
    """Checks if last backup file is less than configured seconds ago."""

    content_type = "db"
    configured_seconds = settings.DBBACKUP_CHECK_SECONDS


class MediaBackupAgeHealthCheck(BaseBackupHealthCheck):
    """Checks if last backup file is less than configured seconds ago."""

    content_type = "media"
    configured_seconds = settings.MEDIABACKUP_CHECK_SECONDS


class BackupJobHealthCheck(BaseHealthCheckBackend):
    """Checks if last backup file is less than configured seconds ago."""

    critical_service = False

    def check_status(self):
        task = TaskResult.objects.filter(task_name="aleksis.core.tasks.backup_data").last()

        # Check if state is success
        if not task:
            self.add_error(_("No backup result found!"))
        elif task and task.status != "SUCCESS":
            self.add_error(f"{task.status} - {task.result}")
