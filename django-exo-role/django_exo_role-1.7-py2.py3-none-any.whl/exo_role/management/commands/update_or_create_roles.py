from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating roles ...'))

        call_command('loaddata', 'categories')
        call_command('loaddata', 'certification_roles')
        call_command('loaddata', '1_roles_exo_sprint')
        call_command('loaddata', '2_roles_fastrack')
        call_command('loaddata', '3_roles_workshop')
        call_command('loaddata', '4_roles_swarm')
        call_command('loaddata', '5_roles_summit')
        call_command('loaddata', '6_roles_ticket')
        call_command('loaddata', '7_roles_talk')
        call_command('loaddata', '8_roles_disruption_session')
        call_command('loaddata', '9_roles_other')
        call_command('loaddata', '10_roles_certification_program')

        self.stdout.write(self.style.SUCCESS('Roles created!'))
