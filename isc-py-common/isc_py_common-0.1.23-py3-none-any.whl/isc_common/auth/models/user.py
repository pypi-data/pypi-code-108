import logging

from bitfield import BitField

from isc_common.auth.managers.user_manager import UserManager
from isc_common.auth.models.abstract_user import AbstractUser
from isc_common.fields.code_field import CodeField
from isc_common.fields.description_field import DescriptionField

logger = logging.getLogger(__name__)


class User(AbstractUser):
    description = DescriptionField(null=True, blank=True)
    color = CodeField(null=True, blank=True)
    props = BitField(flags=(
        ('bot', 'Системный пользователь'),  # 1
    ), default=0, db_index=True)

    @classmethod
    def admin_user(cls):
        admin_user, _ = User.objects.get_or_create(username='admin', defaults=dict(password='admin'))
        return admin_user

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(username="unknown")
        return res

    def __str__(self):
        return f"id: {self.id}, username: {self.username}, full_name: ({self.first_name} {self.middle_name} {self.last_name})"

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        swappable = 'AUTH_USER_MODEL'
