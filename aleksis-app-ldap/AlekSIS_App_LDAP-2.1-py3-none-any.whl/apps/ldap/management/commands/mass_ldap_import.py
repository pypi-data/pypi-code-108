from django.core.management.base import BaseCommand

from ...util.ldap_sync import mass_ldap_import


class Command(BaseCommand):
    def handle(self, *args, **options):
        mass_ldap_import()
