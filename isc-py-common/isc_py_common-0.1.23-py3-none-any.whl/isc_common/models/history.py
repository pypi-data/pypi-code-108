import logging

from django.contrib.postgres.fields import JSONField
from django.db.models import Model, DateTimeField
from django.utils import timezone

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect

logger = logging.getLogger(__name__)


class History(Model):
    date = DateTimeField(db_index=True, default=timezone.now)
    method = CodeField()
    path = CodeField()
    user = ForeignKeyProtect(User)
    data = JSONField(default=dict)

    def __str__(self):
        return f"method: {self.method} path: {self.path} data{self.data}"

    class Meta:
        verbose_name = 'History'
