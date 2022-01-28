from django.core import management

from isc_common.auth.models.user import User


class BaseCommand(management.BaseCommand):
    user = User.objects.get(username='uandrew')
