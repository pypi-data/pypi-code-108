import logging

from django.conf import settings
from django.db import transaction

from events.models.event_types import Event_types
from isc_common import delAttr
from isc_common.auth.models.user import User
from isc_common.bit import IsBitOn, TurnBitOn
from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from twits.models.chat_user_user import Chat_user_user
from twits.models.chats import ChatsManager

logger = logging.getLogger(__name__)


class Event_type_usersQuerySet(AuditQuerySet):
    pass


class Event_type_usersManager(AuditManager):

    @classmethod
    def get_bot(cls, event_type):
        if not isinstance(event_type, Event_types):
            raise Exception(f'event_type must be a Event_types')

        key = 'Event_type_usersManager.get_bot'
        settings.LOCKS.acquire(key)
        bot, _ = User.objects.get_or_create(
            username=f'event_{event_type.code}_bot',
            defaults=dict(
                last_name=f'Бот ({event_type.full_name})',
                password='1234567890',
                props=User.props.bot,
                deliting=False,
                editing=False
            )
        )
        settings.LOCKS.release(key)
        return bot

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'event_type_id': record.event_type.id,
            'user_id': record.user.id,
            'user__username': record.user.username,
            'user__first_name': record.user.first_name,
            'user__last_name': record.user.last_name,
            'user__email': record.user.email,
            'user__middle_name': record.user.middle_name,
            'props': record.user.props._value,
        }
        return res

    def get_queryset(self):
        return Event_type_usersQuerySet(self.model, using=self._db)

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        delAttr(_data, 'id')
        delAttr(_data, 'user__username')
        delAttr(_data, 'user__first_name')
        delAttr(_data, 'user__last_name')
        delAttr(_data, 'user__email')
        delAttr(_data, 'user__middle_name')

        res = super().filter(id=data.get('id')).update(**_data)
        return data

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        user_ids = data.get('user_ids', None)
        context_ids = data.get('context_ids', None)

        with transaction.atomic():
            if user_ids and context_ids:
                if not isinstance(user_ids, list):
                    user_ids = [user_ids]

                if not isinstance(context_ids, list):
                    context_ids = [context_ids]

                for user_id in user_ids:
                    for context_id in context_ids:
                        event_types = Event_types.objects.get(id=context_id)
                        if not IsBitOn(event_types.props, 0):
                            raise Exception(f'Строка: {event_types.full_name} не является событием, и не может подлежать подписке.')
                        res, _ = super().get_or_create(user_id=user_id, event_type_id=context_id)

                        props = 0
                        if IsBitOn(res.event_type.props, 1):
                            props = TurnBitOn(props, 0)
                        chat, created = Chat_user_user.objects.get_or_create(user_reciver_id=user_id, user_sender=Event_type_usersManager.get_bot(res.event_type), defaults=dict(props=props))
                        ChatsManager.refresh_chat_menu(user=User.objects.get(id=user_id), logger=logger)

            return data


class Event_type_users(AuditModel):
    event_type = ForeignKeyCascade(Event_types)
    user = ForeignKeyCascade(User)

    objects = Event_type_usersManager()

    def __str__(self):
        return f"ID:{self.id}, event_type: [{self.event_type}], user: [{self.user}]"

    class Meta:
        verbose_name = 'Подписки на события'
        unique_together = (('event_type', 'user'),)
