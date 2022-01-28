import logging

from django.db import transaction
from django.db.models import PositiveIntegerField, BooleanField
from django.forms import model_to_dict

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.number import DelProps
from tracker.models.messages_theme import Messages_theme
from twits.models.chat_user_user import Chat_user_userManager

logger = logging.getLogger(__name__)


class Chat_user_userViewQuerySet(AuditQuerySet):
    def create(self, **kwargs):
        from twits.models.chat_user_user_theme import Chat_user_user_theme

        user_sender = User.objects.get(id=kwargs.get('user_sender_id'))
        user_reciver = User.objects.get(id=kwargs.get('user_reciver_id'))

        if user_sender.id == user_reciver.id:
            raise Exception(f'Чат с самим собою не допускается.')

        try:
            common = self.model.objects.get(user_sender=user_sender, user_reciver=user_reciver)
        except self.model.DoesNotExist:
            try:
                common = self.model.objects.get(user_sender=user_reciver, user_reciver=user_sender)
            except self.model.DoesNotExist:
                common = None

        if common:
            setAttr(kwargs, 'common_id', common.id)

        with transaction.atomic():
            theme, created = Messages_theme.objects.get_or_create(
                code=f'tetatet_{user_sender.get_short_name}_{user_reciver.get_short_name}',
                defaults=dict(
                    name=f'Чат: {user_sender.get_short_name} : {user_reciver.get_short_name}',
                    creator=User.admin_user(),
                    editing=False,
                    deliting=False,
                    parent=Messages_theme.tetatet_chats_theme(),
                    description='Группа создана автоматически'))

            chat_user_user = super().create(**kwargs)

            Chat_user_user_theme.objects.get_or_create(theme=theme, chat_user_user=chat_user_user)
            if not common:
                chat_user_user.common_id = chat_user_user.id
                chat_user_user.save()
        return chat_user_user

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Chat_user_userViewManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'common_id': record.common_id,
            'user_sender_id': record.user_sender.id,
            'user_reciver_id': record.user_reciver.id,
            'user_reciver__username': record.user_reciver.username,
            'user_reciver__first_name': record.user_reciver.first_name,
            'user_reciver__last_name': record.user_reciver.last_name,
            'user_reciver__email': record.user_reciver.email,
            'user_reciver__middle_name': record.user_reciver.middle_name,
            'user_reciver__last_login': record.user_reciver.last_login,
            'props': record.props,
            'compulsory_reading': record.props.compulsory_reading,
        }
        return DelProps(res)

    def get_queryset(self):
        return Chat_user_userViewQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        user_ids = data.get('user_ids', None)
        context_ids = data.get('context_ids', None)
        _data = []

        if user_ids and context_ids:
            if not isinstance(user_ids, list):
                user_ids = [user_ids]

            if not isinstance(context_ids, list):
                context_ids = [context_ids]

            for user_id in user_ids:
                for user_sender_id in context_ids:
                    res = super().create(user_reciver_id=user_id, user_sender_id=user_sender_id)
                    _data.append(model_to_dict(res))

        return data


class Chat_user_userView(AuditModel):
    user_sender = ForeignKeyCascade(User, related_name='user_sender_user_view')
    user_reciver = ForeignKeyCascade(User, related_name='user_reciver_user_view')
    common_id = PositiveIntegerField()
    props = Chat_user_userManager.props()

    objects = Chat_user_userViewManager()

    def __str__(self):
        return f'id: {self.id}, common_id: {self.common_id}, user_sender: [{self.user_sender}], user_reciver: [{self.user_reciver}]'

    class Meta:
        verbose_name = 'Чаты личной переписки'
        managed = False
        db_table = 'twits_chat_user_user_view'
