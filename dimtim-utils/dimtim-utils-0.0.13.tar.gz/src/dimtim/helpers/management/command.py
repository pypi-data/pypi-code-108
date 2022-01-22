import sys
from argparse import ArgumentParser

from dimtim.helpers.logger import Logger


class CommandError(Exception):
    pass


class CommandBase:
    help = '...'

    def __init__(self, runner_path: str):
        self.stdin, self.stdout, self.stderr = sys.stdin, sys.stdout, sys.stderr

        self.name = self.__module__.split('.')[-1]
        self.runner_path = runner_path
        self.logger = Logger('management', f'{self.name}: ', self.stdout)

    def add_arguments(self, parser: ArgumentParser):
        pass

    def run(self, args):
        parser = ArgumentParser(description=self.help)
        self.add_arguments(parser)
        args = vars(parser.parse_args(args))
        try:
            self.handle(**args)
        except KeyboardInterrupt:
            sys.stderr.write(f'Commad interrupted...\n')
        except CommandError as e:
            sys.stderr.write(f'{str(e)}\n')

    def handle(self, **kwargs):
        raise NotImplementedError('A subclass of the CommandBase class must implement the "handle" method!')
