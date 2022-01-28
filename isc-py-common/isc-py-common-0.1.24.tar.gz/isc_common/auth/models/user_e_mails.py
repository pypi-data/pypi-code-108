import logging

from bitfield import BitField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from isc_common.models.e_mails import E_mails, Model_e_mailQuerySet

logger = logging.getLogger(__name__)


class User_e_mailsQuerySet(Model_e_mailQuerySet):
    pass


class User_e_mailsManager(AuditManager):
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
        return User_e_mailsQuerySet(self.model, using=self._db)


class User_e_mails(AuditModel):
    code = CodeStrictField()
    user = ForeignKeyProtect(User)
    e_mail = ForeignKeyProtect(E_mails)
    props = User_e_mailsManager.props()

    objects = User_e_mailsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Администрация клуба'
        unique_together = (('code', 'user', 'e_mail'),)
