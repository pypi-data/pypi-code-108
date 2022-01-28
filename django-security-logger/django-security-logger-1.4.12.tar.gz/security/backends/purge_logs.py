from datetime import timedelta

from django.core.management.base import CommandError
from django.core.management.base import BaseCommand
from django.utils.timezone import now


UNIT_OPTIONS = {
    'h': lambda amount: now() - timedelta(hours=amount),
    'd': lambda amount: now() - timedelta(days=amount),
    'w': lambda amount: now() - timedelta(weeks=amount),
    'm': lambda amount: now() - timedelta(days=(30 * amount)),  # 30-day month
    'y': lambda amount: now() - timedelta(weeks=(52 * amount)),  # 364-day year
}


class Command(BaseCommand):

    models = {}

    def add_arguments(self, parser):
        parser.add_argument('--type', action='store', dest='type', default='input-request',
                            help='Tells Django what type of requests should be removed '
                                 '({}).'.format('/'.join(self.models.keys())))
        parser.add_argument('--expiration', action='store', dest='expiration',
                            help='Sets the timedelta from which logs will be removed.', required=True)
        parser.add_argument('--noinput', action='store_false', dest='interactive', default=True,
                            help='Tells Django to NOT prompt the user for input of any kind.')

    def _clean_data(self, qs, options):
        raise NotImplementedError

    def _get_queryset(self, model, timestamp):
        raise NotImplementedError

    def _get_qs_count(self, qs):
        raise NotImplementedError

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

        model = self._get_model(type)
        qs = self._get_queryset(model, UNIT_OPTIONS[unit](amount))
        if self._get_qs_count(qs) == 0:
            self.stdout.write('There are no logs to delete.')
        else:
            if options.get('interactive'):
                confirm = input('''
                   You have requested a database reset.
                   This will IRREVERSIBLY DESTROY any
                   logs created before {} {}
                   ago. That is a total of {} logs.
                   Are you sure you want to do this?
                   Type 'yes' to continue, or 'no' to cancel: '''.format(amount, unit, qs.count()))
            else:
                confirm = 'yes'

            if confirm == 'yes':
                self.stdout.write('Clean data')
                self._clean_data(qs, options)

    def _get_model(self, type):
        model = self.models.get(type)
        if model:
            return model
        else:
            raise CommandError('Type can be only one of "{}"'.format('/'.join(self.models.keys())))
