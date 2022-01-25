import logging

from django.db import models
from django.utils import timezone

from puddl.contrib.file.models import File
from .lib import iter_bash_history
from puddl.models import Datum

log = logging.getLogger(__name__)


class BashHistoryManager(models.Manager):

    def from_file(self, file: File):
        with file.path.open() as f:
            rows = iter_bash_history(f)
            instances = []
            for ts, command_line in rows:
                instances.append(self.model(
                    file=file,
                    dt=timezone.datetime.fromtimestamp(ts),
                    command=command_line,
                ))
            return self.bulk_create(instances)


class BashHistory(Datum):
    objects = BashHistoryManager()

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    dt = models.DateTimeField()
    command = models.TextField()

    class Meta:
        db_table = 'bash_history'

    def __str__(self):
        return f'{self.file}@{self.dt}'
