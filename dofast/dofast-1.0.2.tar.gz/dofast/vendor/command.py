#!/usr/bin/env python
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Union, Dict

import codefast as cf

cf.logger.level = 'info'
import warnings


class Executor:
    @staticmethod
    def run_in_order(processors: List[Tuple[str]], input_args: dict) -> None:
        '''Supports sequential execution of multiple subcommands.
        :processors: List of functions
        :input_args: dict of arguments to pass to related function in processors
        '''
        for method_name, value in input_args.items():
            method_body = processors[method_name]
            argcount = method_body.__code__.co_argcount
            if len(value) > argcount:
                warnings.warn(
                    f'[{method_name}] has more arguments than the function body.')
            value = value[:argcount-1]
            if value:
                method_body(value)
            else:
                method_body(None)


class Command(ABC):
    def __init__(self):
        self.name = 'base'
        self.arguments = defaultdict(list)
        self.subcommands = []
        self.description = self.name + ' command'

    def __str__(self):
        return '\n'.join((f'{k}: {v}' for k, v in self.__dict__.items()))

    def execute(self):
        Executor.run_in_order(self.get_processors, self.arguments)

    @property
    def get_processors(self) -> Dict[str, str]:
        """Return a dict of processors for this command.
        key: subcommand name
        value: self.method_name
        """
        long_commands = [sorted(sc, key=len)[-1] for sc in self.subcommands]
        _ps = {e: getattr(self, e, lambda: id) for e in long_commands}
        _ps[self.name] = getattr(self, '_process', lambda: id)
        return _ps

    def disassemble_input_arguments(self, args):
        '''parse input arguments'''
        _aliases = CommandParser.make_aliases(self.subcommands)
        if self.name not in _aliases:
            _aliases[self.name] = self.name
        pre_arg = _aliases[self.name]
        
        if not args:
            # There is no subcommands and subargs passed in
            self.arguments[pre_arg]=[]

        for arg in args:
            if arg.startswith('-'):
                pre_arg = _aliases[arg.replace('-', '')]
                self.arguments[pre_arg] = []
            else:
                self.arguments[pre_arg].append(arg)

    def run(self, args: List[str]):
        self.disassemble_input_arguments(args)
        self.execute()

    def describe_self(self):
        '''Display class's usage message.'''
        print(' {:<19} {}'.format(cf.fp.magenta(self.name), self.description))
        if self.subcommands:
            print('{:<21} {}'.format('', 'Subcommmands:'))
        for lst in self.subcommands:
            lst = sorted(lst, key=len, reverse=True)
            s = cf.fp.green('-' + lst[0])
            if len(lst) > 1:
                s += ' (or ' + ' | '.join(
                    map(lambda x: cf.fp.cyan('-' + x), lst[1:])) + ')'
            print('{:<22} {}'.format('', s))


class CommandParser:
    @staticmethod
    def make_aliases(subcommmands: List[List[str]]) -> dict:
        aliases = {}
        for lst in subcommmands:
            lst.sort(key=len, reverse=True)
            for s in lst:
                aliases[s] = lst[0]
        return aliases


class HelpCommand(Command):
    def execute(self):
        print(self)


class Context:
    def __init__(self):
        self.commands = {}
        self.uniq_commands = {}  # For displaying help message

    def add_command(self, name: Union[str, List[str]],
                    command: Command) -> None:
        if isinstance(name, str):
            self.commands[name] = command
            self.uniq_commands[name] = command
        else:
            name.sort(key=len, reverse=True)
            self.uniq_commands[name[0]] = command
            for n in name:
                self.commands[n] = command

    def get_command(self, name):
        return self.commands.get(name, HelpCommand)

    def display_help_message(self):
        for _, v in self.uniq_commands.items():
            obj = v()
            obj.describe_self()

    def execute(self):
        args = sys.argv[1:]
        main_command = args[0].replace('-', '') if args else 'help'
        if main_command == 'help':
            self.display_help_message()
        else:
            StrategyClass = self.get_command(main_command)
            StrategyClass().run(args[1:])
