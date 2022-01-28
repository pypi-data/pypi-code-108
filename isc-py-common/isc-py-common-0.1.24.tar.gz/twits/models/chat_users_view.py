import logging

from bitfield import BitField
from django.db.models import BooleanField
from django.forms import model_to_dict

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from isc_common.number import DelProps
from twits.models.chat_users import Chat_usersManager
from twits.models.chats import Chats

logger = logging.getLogger(__name__)


class Chat_usersViewQuerySet(AuditQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Chat_usersViewManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            "user_id": record.user.id,
            "chat_id": record.chat.id,
            "user__username": record.user.username,
            "user__first_name": record.user.first_name,
            "user__last_name": record.user.last_name,
            "user__email": record.user.email,
            "user__middle_name": record.user.middle_name,
            'props': record.props,
            'compulsory_reading': record.props.compulsory_reading,
            'relevant': record.props.relevant,
            'readonly': record.props.readonly,
        }
        return DelProps(res)

    def get_queryset(self):
        return Chat_usersViewQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        user_ids = data.get('user_ids', None)
        context_ids = data.get('context_ids', None)
        _data=[]

        if user_ids and context_ids:
            if not isinstance(user_ids, list):
                user_ids = [user_ids]

            if not isinstance(context_ids, list):
                context_ids = [context_ids]

            for user_id in user_ids:
                for chat_id in context_ids:
                    res = super().create(user_id=user_id, chat_id=chat_id)
                    _data.append(model_to_dict(res))

        return data


class Chat_usersView(AuditModel):
    user = ForeignKeyCascade(User)
    chat = ForeignKeyCascade(Chats)
    props = Chat_usersManager.props()
    compulsory_reading = BooleanField()
    relevant = BooleanField()
    readonly = BooleanField()

    objects = Chat_usersViewManager()

    def __str__(self):
        return f"id: {self.id}, user: [{self.user}] chat: [{self.chat}]"

    class Meta:
        verbose_name = 'Участники чатов'
        unique_together = (('user', 'chat'),)
        managed = False
        db_table = 'twits_chat_users_view'
