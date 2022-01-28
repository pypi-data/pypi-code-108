import logging

from django.contrib.postgres.fields import ArrayField
from django.db.models import BooleanField, BigIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_tree_grid_manager import CommonTreeGridManager
from isc_common.models.audit import AuditQuerySet
from isc_common.models.base_ref import BaseRefHierarcy

logger = logging.getLogger(__name__)


class Messages_theme_viewQuerySet(AuditQuerySet):
    def get_range_rows1(self, request, function):
        request = DSRequest(request=request)
        criteria = request.get_criteria()
        if isinstance(criteria, list):
            criteria = [l for l in request.get_criteria() if l.get('fieldName') != 'user_id']
        request.set_criteria(criteria=criteria)
        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        return self.get_range_rows(start=request.startRow, end=request.endRow, function=function, json=request.json)


class Messages_theme_view_Manager(CommonTreeGridManager):
    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            # 'full_name': record.full_name,
            'description': record.description,
            'parent_id': record.parent_id,
            'lastmodified': record.lastmodified,
            'isFolder': record.isFolder,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Messages_theme_viewQuerySet(self.model, using=self._db)


class Messages_theme_view(BaseRefHierarcy):
    users = ArrayField(BigIntegerField(), default=list)
    creator = ForeignKeyCascade(User, null=True, blank=True, related_name='creator_theme')
    isFolder = BooleanField(default=False)

    def __str__(self):
        return f'{self.code}: {self.name}'

    objects = Messages_theme_view_Manager()

    class Meta:
        verbose_name = 'Темы задач'
        managed = False
        db_table = 'tracker_messages_theme_view'
