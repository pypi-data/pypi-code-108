import logging

from isc_common.fields.code_field import CodeStrictField
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class Model_e_mailQuerySet(AuditQuerySet):

    def update_or_create(self, defaults=None, **kwargs):
        e_mail = defaults.get('e_mail')

        if e_mail != '' and e_mail is not None:
            e_mail_item = E_mails.objects.getOptional(e_mail=e_mail)
            if e_mail_item is None:
                try:
                    item = super().get(**kwargs)
                    e_mail_item, _ = E_mails.objects.update_or_create(id=item.e_mail.id, defaults=dict(e_mail=e_mail))
                except self.model.DoesNotExist:
                    e_mail_item = E_mails.objects.create(e_mail=e_mail)
            defaults = dict(e_mail=e_mail_item)
            return super().update_or_create(defaults=defaults, **kwargs)
        else:
            return None, None


class E_mailsQuerySet(AuditQuerySet):
    pass


class E_mailsManager(AuditManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return E_mailsQuerySet(self.model, using=self._db)


class E_mails(AuditModel):
    e_mail = CodeStrictField(unique=True)
    objects = E_mailsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Почтовые адреса'
