import logging

from isc_common.auth.models.user import User
from isc_common.fields.code_field import JSONFieldIVC
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel
from permission.models.widgets_trees import Widgets_trees

logger = logging.getLogger( __name__ )


class User_permission( AuditModel ) :
    user = ForeignKeyCascade( User )
    widget = ForeignKeyCascade( Widgets_trees )
    permission = JSONFieldIVC()

    def __str__( self ) :
        return f"{self.user.username}: {self.widget.id_widget}"

    class Meta :
        verbose_name = 'Доступы для пользователей'
        unique_together = (("user" , "widget") ,)
