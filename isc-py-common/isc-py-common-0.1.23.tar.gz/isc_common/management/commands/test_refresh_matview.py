import logging

from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from isc_common.common.mat_views import refresh_mat_view

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        # parser.add_argument('--message', type=str)

    def handle(self, *args, **options):
        username = options.get('username')
        user = User.objects.get(username=username)
        # message = options.get('message')

        refresh_mat_view('kd_documents_mview', username)
        print("Done.")

        refresh_mat_view('kd_documents_mview', username)
        print("Done.")
