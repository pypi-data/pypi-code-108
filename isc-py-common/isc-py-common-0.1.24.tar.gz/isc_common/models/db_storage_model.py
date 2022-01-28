from django.db.models import BinaryField, TextField

from isc_common.fields.code_field import CodeField
from isc_common.models.audit import AuditModel


class DbStorage(AuditModel):
    blob = BinaryField()
    filename = TextField(unique=True)
    mimetype = CodeField()

    class Meta:
        abstract = True
