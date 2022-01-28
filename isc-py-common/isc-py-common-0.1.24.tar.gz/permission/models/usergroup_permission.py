import logging

from isc_common.auth.models.usergroup import UserGroup
from isc_common.fields.code_field import JSONFieldIVC
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel
from permission.models.widgets_trees import Widgets_trees

logger = logging.getLogger( __name__ )


class Usergroup_permission( AuditModel ) :
    usergroup = ForeignKeyCascade( UserGroup )
    widget = ForeignKeyCascade( Widgets_trees )
    permission = JSONFieldIVC()

    # def __str__(self):
    #     return f"{self.code}: {self.name}"

    class Meta :
        verbose_name = 'Доступы для групп'
        unique_together = (("usergroup" , "widget") ,)
