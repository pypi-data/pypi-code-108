import logging

from isc_common.fields.code_field import CodeStrictField
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel

logger = logging.getLogger(__name__)


class Model_phonesQuerySet(AuditQuerySet):

    def update_or_create(self, defaults=None, **kwargs):
        phone = defaults.get('phone')

        if phone != '' and phone is not None:
            phone_item = Phones.objects.getOptional(phone=phone)
            if phone_item is None:
                try:
                    item = super().get(**kwargs)
                    phone_item, _ = Phones.objects.update_or_create(id=item.phone.id, defaults=dict(phone=phone))
                except self.model.DoesNotExist:
                    phone_item = Phones.objects.create(phone=phone)
            defaults = dict(phone=phone_item)
            return super().update_or_create(defaults=defaults, **kwargs)
        else:
            return None, None


class PhonesQuerySet(AuditQuerySet):
    pass


class PhonesManager(AuditManager):

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'id': record.id,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return PhonesQuerySet(self.model, using=self._db)


class Phones(AuditModel):
    phone = CodeStrictField(unique=True)
    objects = PhonesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Телефоны'
