import logging

from bitfield import BitField
from django.db import transaction

from isc_common import setAttr, delAttr
from isc_common.auth.models.user import User
from isc_common.bit import IsBitOn
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager
from tracker.models.messages_theme import Messages_theme

logger = logging.getLogger(__name__)


class MessagesThemeUsersAccessQuerySet(AuditQuerySet):
    pass


class MessagesThemeUsersAccessManager(AuditManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'theme_id': record.theme.id,
            'user_id': record.user.id,
            'user__username': record.user.username,
            'user__first_name': record.user.first_name,
            'user__last_name': record.user.last_name,
            'user__email': record.user.email,
            'user__middle_name': record.user.middle_name,
            'props': record.user.props._value,
            'all_content': IsBitOn(record.props._value, 0)
        }
        return res

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        props = _data.get('props')

        if data.get('all_content') is True:
            props |= MessagesThemeUsersAccess.props.all_content
        else:
            props &= ~MessagesThemeUsersAccess.props.all_content

        setAttr(_data, 'props', props)
        delAttr(_data, 'id')
        delAttr(_data, 'user__username')
        delAttr(_data, 'user__first_name')
        delAttr(_data, 'user__last_name')
        delAttr(_data, 'user__email')
        delAttr(_data, 'user__middle_name')
        delAttr(_data, 'all_content')

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
                        res, _ = super().get_or_create(user_id=user_id, theme_id=context_id)

            return data

    def get_queryset(self):
        return MessagesThemeUsersAccessQuerySet(self.model, using=self._db)


class MessagesThemeUsersAccess(AuditModel):
    theme = ForeignKeyCascade(Messages_theme)
    user = ForeignKeyCascade(User)
    props = BitField(flags=(
        ('all_content', 'Доступ ко всем делам данной темы'),  # 1
    ), default=0, db_index=True)

    objects = MessagesThemeUsersAccessManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Доступы к темам'
