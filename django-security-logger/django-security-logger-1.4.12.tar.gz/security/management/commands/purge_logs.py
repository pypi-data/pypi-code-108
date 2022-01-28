from datetime import timedelta

from django.core.management.base import CommandError
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from security.enums import LoggerName
from security.backends.writer import clean_logs


UNIT_OPTIONS = {
    'h': lambda amount: now() - timedelta(hours=amount),
    'd': lambda amount: now() - timedelta(days=amount),
    'w': lambda amount: now() - timedelta(weeks=amount),
    'm': lambda amount: now() - timedelta(days=(30 * amount)),  # 30-day month
    'y': lambda amount: now() - timedelta(weeks=(52 * amount)),  # 364-day year
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--type', action='store', dest='type', default='input-request',
                            help='Tells Django what type of requests should be removed '
                                 '({}).'.format('/'.join([logger.value for logger in LoggerName])))
        parser.add_argument('--expiration', action='store', dest='expiration',
                            help='Sets the timedelta from which logs will be removed.', required=True)
        parser.add_argument('--noinput', action='store_false', dest='interactive', default=True,
                            help='Tells Django to NOT prompt the user for input of any kind.')
        parser.add_argument('--backup', action='store', dest='backup', default=False,
                            help='Tells Django where to backup removed logs.')

    def handle(self, expiration, type, **options):
        # Check we have the correct values
        unit = expiration[-1]
        amount = expiration[0:-1]
        try:
            amount = int(amount)
        except ValueError:
            raise CommandError('Invalid expiration format')

        if unit not in UNIT_OPTIONS:
            raise CommandError('Invalid expiration format')

        try:
            type = LoggerName(type)
        except KeyError:
            raise CommandError('Type can be only one of "{}"'.format('/'.join([logger.value for logger in LoggerName])))

        if options.get('interactive'):
            confirm = input('''
               You have requested a database reset.
               This will IRREVERSIBLY DESTROY any
               logs created before {} {}
               ago. Are you sure you want to do this?
               Type 'yes' to continue, or 'no' to cancel: '''.format(amount, unit))
        else:
            confirm = 'yes'

        if confirm == 'yes':
            self.stdout.write('Clean data')
            clean_logs(type, UNIT_OPTIONS[unit](amount), options.get('backup'), self.stdout)
