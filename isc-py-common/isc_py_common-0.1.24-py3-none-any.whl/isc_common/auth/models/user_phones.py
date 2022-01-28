import logging

from bitfield import BitField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from isc_common.models.phones import Phones, Model_phonesQuerySet

logger = logging.getLogger(__name__)


class User_phonesQuerySet(Model_phonesQuerySet):
    pass


class User_phonesManager(AuditManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('main', 'Главная'),  # 1
        ), default=0, db_index=True)

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return User_phonesQuerySet(self.model, using=self._db)


class User_phones(AuditModel):
    code = CodeStrictField()
    user = ForeignKeyProtect(User)
    phone = ForeignKeyProtect(Phones)
    props = User_phonesManager.props()

    objects = User_phonesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Администрация клуба'
        unique_together = (('code', 'user', 'phone'),)
