from argparse import Namespace

from django.core.management.base import BaseCommand

from dbsamizdat.runner import augment_argument_parser
from dbsamizdat.exceptions import SamizdatException


class Command(BaseCommand):
    help = 'Play nice with dbsamizdat.'

    def create_parser(self, *args, **kwargs):
        return super(Command, self).create_parser(*args, **{**kwargs, **{'conflict_handler': 'resolve'}})

    def add_arguments(self, parser):
        augment_argument_parser(parser, in_django=True, log_rather_than_print=False)

    def handle(self, *args, **options):
        try:
            options['func'](Namespace(**options))
        except SamizdatException as argh:
            exit(f'\n\n\nFATAL: {argh}')
        except KeyboardInterrupt:
            exit('\nInterrupted.')
