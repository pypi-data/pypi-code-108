import logging

from django.db.models import BooleanField

from isc_common import delAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_tree_grid_manager import CommonTreeGridManager
from isc_common.models.base_ref import BaseRefHierarcy

logger = logging.getLogger(__name__)


class Messages_theme_admin_view_Manager(CommonTreeGridManager):
    @classmethod
    def getRecord(cls, record):
        res = {
            "id": record.id,
            "code": record.code,
            "name": record.name,
            # "full_name": record.full_name,
            "description": record.description,
            "parent_id": record.parent_id,
            "lastmodified": record.lastmodified,
            "isFolder": record.isFolder,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

class Messages_theme_admin_view(BaseRefHierarcy):
    creator = ForeignKeyCascade(User, null=True, blank=True, related_name='creator_theme_admin')
    isFolder = BooleanField(default=False)

    def __str__(self):
        return f"{self.code}: {self.name}"

    objects = Messages_theme_admin_view_Manager()

    class Meta:
        verbose_name = 'Темы задач'
        managed = False
        db_table = 'tracker_messages_theme_admin_view'
