import logging

from django.db.models import DateTimeField, BooleanField, UUIDField
from django.utils import timezone

from isc_common.auth.models.user import User
from isc_common.bit import IsBitOff
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel
from tracker.models.messages import MessagesManager, MessagesQuerySet
from tracker.models.messages_importance import Messages_importance
from tracker.models.messages_state import Messages_state
from tracker.models.messages_theme import Messages_theme

logger = logging.getLogger(__name__)


class Messages_viewQuerySet(MessagesQuerySet):
    def get_range_rows1(self, request, function = None, distinct_field_names = None):
        request = DSRequest(request = request)
        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        return self.get_range_rows3(start = request.startRow, end = request.endRow, function = function, distinct_field_names = distinct_field_names, json = request.json)


class Messages_viewManager(MessagesManager):

    @classmethod
    def getRecord(cls, record, enabled = None):
        res = {
            'date_create': record.date_create,
            'deliting': record.deliting,
            'editing': record.editing,
            'guid': str(record.guid).upper() if record.guid else None,
            'id': record.id,
            'isFolder': record.isFolder,
            'lastmodified': record.lastmodified,
            'message': record.message,
            'parent_id': record.parent_id,
            'state__name': record.state.name,
            'state_id': record.state.id,
            'theme__full_name': record.theme.full_name,
            'theme__name': record.theme.full_name,
            'theme_id': record.theme.id,
            'importance_id': record.importance.id if record.importance else None,
            'importance__code': record.importance.code if record.importance else None,
            'importance__name': record.importance.name if record.importance else None,
            'to_whom_id': record.to_whom.id,
            'to_whom__short_name': record.to_whom.get_short_name,
            'user__short_name': record.user.get_short_name,
            'user__username': record.user.username,
            'user_id': record.user.id if record.user else None,
            'enabled': IsBitOff(record.state.props, 0),
        }
        return res

    def get_queryset(self):
        return Messages_viewQuerySet(self.model, using = self._db)


class Messages_view(AuditModel):
    guid = UUIDField(blank = True, null = True)
    date_create = DateTimeField(verbose_name = 'Дата записи', db_index = True, default = timezone.now)
    isFolder = BooleanField(default = False)
    all_content = BooleanField(default = False)
    message = DescriptionField('Тело задач', null = False, blank = False)
    parent = ForeignKeyProtect('self', blank = True, null = True)
    state = ForeignKeyProtect(Messages_state)
    theme = ForeignKeyProtect(Messages_theme)
    user = ForeignKeyCascade(User, related_name = 'user_view')
    tma_user = ForeignKeyCascade(User, related_name = 'tma_user_view')
    to_whom = ForeignKeyCascade(User, related_name = 'user_to_whom')
    importance = ForeignKeyProtect(Messages_importance, blank = True, null = True)

    def __str__(self):
        return f'id: {self.id}, guid: {str(self.guid).upper()}, message: {self.message}, date_create: {self.date_create}, user: [{self.user}], theme: [{self.theme}], state: [{self.state}]'

    objects = Messages_viewManager()

    class Meta:
        managed = False
        db_table = 'tracker_messages_view'
        verbose_name = 'Сообщения'
