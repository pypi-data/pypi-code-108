import logging

from bitfield import BitField
from django.db import transaction
from django.forms import model_to_dict

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from isc_common.number import DelProps
from twits.models.chats import Chats, ChatsManager

logger = logging.getLogger(__name__)


class Chat_usersQuerySet(AuditQuerySet):

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Chat_usersManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'chat_id': record.chat.id,
            'user_id': record.user.id,
            'user__username': record.user.username,
            'user__first_name': record.user.first_name,
            'user__last_name': record.user.last_name,
            'user__email': record.user.email,
            'user__middle_name': record.user.middle_name,
            'props': record.props,
            'compulsory_reading': record.props.compulsory_reading,
            'relevant': record.props.relevant,
            'readonly': record.props.readonly,
        }
        return DelProps(res)

    def get_queryset(self):
        return Chat_usersQuerySet(self.model, using=self._db)

    def createFromRequest(self, request, removed=None):
        request = DSRequest(request=request)
        data = request.get_data()
        user_ids = data.get('user_ids', None)
        context_ids = data.get('context_ids', None)
        _data = []

        with transaction.atomic():
            if user_ids and context_ids:
                if not isinstance(user_ids, list):
                    user_ids = [user_ids]

                if not isinstance(context_ids, list):
                    context_ids = [context_ids]

                for user_id in user_ids:
                    for chat_id in context_ids:
                        res = super().create(user_id=user_id, chat_id=chat_id)

                        ChatsManager.refresh_chat_menu(user=res.user, logger=logger)
                        _data.append(model_to_dict(res))

            return data

    def updateFromRequest(self, request, removed=None, function=None):
        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()

        with transaction.atomic():
            props = data.get('props')
            if data.get('compulsory_reading') is True:
                props |= Chat_users.props.compulsory_reading
            else:
                props &= ~Chat_users.props.compulsory_reading

            if data.get('relevant') is True:
                props |= Chat_users.props.relevant
            else:
                props &= ~Chat_users.props.relevant

            if data.get('readonly') is True:
                props |= Chat_users.props.readonly
            else:
                props &= ~Chat_users.props.readonly

            _data = dict()
            setAttr(_data, 'props', props)

            res, _ = super().update_or_create(id=data.get('id'), defaults=_data)
            ChatsManager.refresh_chat_menu(user=res.user, logger=logger)

            return data

    def deleteFromRequest(self, request, removed=None, ):
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_tuple_ids()
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    super().filter(id=id).soft_delete()
                elif mode == 'visible':
                    super().filter(id=id).soft_restore()
                else:
                    chat_users = super().get(id=id)
                    chat_users.delete()
                    qty = 1

                    ChatsManager.refresh_chat_menu(user=chat_users.user, logger=logger)
                res += qty

            return res

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('compulsory_reading', 'Обязательное прочтение'),  # 1
            ('relevant', 'Актуальность'),  # 2
            ('readonly', 'Только чтение'),  # 4
        ), default=0, db_index=True)


class Chat_users(AuditModel):
    user = ForeignKeyCascade(User)
    chat = ForeignKeyCascade(Chats)
    props = Chat_usersManager.props()

    objects = Chat_usersManager()

    def __str__(self):
        return f"id: {self.id}, user: [{self.user}] chat: [{self.chat}]"

    class Meta:
        verbose_name = 'Участники чатов'
        unique_together = (('user', 'chat'),)
