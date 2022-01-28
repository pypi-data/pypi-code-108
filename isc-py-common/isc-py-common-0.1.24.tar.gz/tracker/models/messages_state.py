import logging

from bitfield import BitField

from isc_common.bit import IsBitOn
from isc_common.models.base_ref import BaseRef, BaseRefQuerySet, StatusBaseRefManager

logger = logging.getLogger(__name__)


class Messages_stateQuerySet(BaseRefQuerySet):
    pass

class Messages_stateManager(StatusBaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'props': record.props._value,
            'disabled': IsBitOn(record.props, 0),
        }
        return res

    def get_queryset(self):
        return Messages_stateQuerySet(self.model, using=self._db)


class Messages_state(BaseRef):
    props = BitField(flags=(
        ('disabled', 'Неактивная запись в гриде')
    ), default=0, db_index=True)

    objects = Messages_stateManager()

    def __str__(self):
        return f"id: {self.code}, id: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Состояние задачи'

    @classmethod
    def message_state_new(cls):
        return Messages_state.objects.update_or_create(code="new", defaults=dict(name='Новый'))[0]

    @classmethod
    def message_state_closed(cls):
        return Messages_state.objects.update_or_create(code="closed", defaults=dict(name='Закрыто'))[0]

    @classmethod
    def message_state_delivered(cls):
        return Messages_state.objects.update_or_create(code="delivered", defaults=dict(name='Доставлено'))[0]

    @classmethod
    def message_state_readed(cls):
        return Messages_state.objects.update_or_create(code="readed", defaults=dict(name='Прочитано'))[0]

    @classmethod
    def message_state_not_readed(cls):
        return Messages_state.objects.get_or_create(code="delivered_not_readed", defaults=dict(name='Доставлено (Не прочитано)'))[0]
