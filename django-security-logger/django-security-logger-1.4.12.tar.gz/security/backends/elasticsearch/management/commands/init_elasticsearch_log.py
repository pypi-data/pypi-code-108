from django.core.management.base import BaseCommand, CommandError

from security.backends.elasticsearch.connection import set_connection
from security.backends.elasticsearch.models import (
    InputRequestLog, OutputRequestLog, CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )

    def handle(self, **options):
        if options['interactive']:
            message = (
                'This will delete existing logs!\n'
                'Are you sure you want to do this?\n\n'
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input(message) != 'yes':
                raise CommandError('Init elasticsearch logs cancelled.')

        self.stdout.write('Init elasticsearch logs')
        set_connection(init_documents=False)
        for document in InputRequestLog, OutputRequestLog, CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog:
            document._index.delete(ignore=404)
            document.init()
