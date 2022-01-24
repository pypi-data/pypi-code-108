from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, **options):
        for i in range(10):
            self.stdout.write(f'STDOUT row {i}')
        for i in range(10):
            self.stderr.write(f'STDERR row {i}')
