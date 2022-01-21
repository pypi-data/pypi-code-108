import datetime
import uuid

from djongo import models


class AuditoryModel(models.Model):
    __abstract__ = True

    created_by = models.UUIDField(default=uuid.uuid4)
    created_date = models.DateTimeField(default=datetime.datetime.now)
    updated_by = models.UUIDField(default=uuid.uuid4)
    updated_date = models.DateTimeField(default=datetime.datetime.now)
