#!/usr/bin/env python
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Union, Dict

from codefast import fp
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
            # Method arguments MUST be passed as a List, the method itself handles the conversion
            method_body(value)


class AbstractClient(ABC):
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
        aliases = CommandParser.make_aliases(self.subcommands)
        if self.name not in aliases:
            aliases[self.name] = self.name
        pre_arg = aliases[self.name]
        for arg in args:
            if arg.startswith('-'):
                current_arg_name = arg.replace('-', '')
                if current_arg_name not in aliases:
                    print(f'[{fp.red(arg)}] is not a valid argument.\n')
                    self.describe_self()
                    sys.exit(1)
                pre_arg = aliases[current_arg_name]
                self.arguments[pre_arg] = []
            else:
                self.arguments[pre_arg].append(arg)

    def run(self, args: List[str]):
        self.disassemble_input_arguments(args)
        self.execute()

    def describe_self(self):
        '''Display class's usage message.'''
        print('\n{:<19} {}'.format(fp.magenta(self.name), self.description))
        if self.subcommands:
            print('{:<13} {}'.format('', 'Subcommmands:'))
        for lst in self.subcommands:
            lst = sorted(lst, key=len, reverse=True)
            s = fp.green('-' + lst[0])
            if len(lst) > 1:
                s += ' (or ' + ' | '.join(
                    map(lambda x: fp.cyan('-' + x), lst[1:])) + ')'
            print('{:<13} {}'.format('', s))


class CommandParser:
    @staticmethod
    def make_aliases(subcommmands: List[List[str]]) -> dict:
        aliases = {}
        for lst in subcommmands:
            lst.sort(key=len, reverse=True)
            for s in lst:
                aliases[s] = lst[0]
        return aliases


class HelpClient(AbstractClient):
    def execute(self):
        print(self)


class Context:
    def __init__(self):
        self.commands = {}
        self.uniq_commands = {}  # For displaying help message

    def add_command(self, name: Union[str, List[str]],
                    command: AbstractClient) -> None:
        if isinstance(name, str):
            self.commands[name] = command
            self.uniq_commands[name] = command
        else:
            name.sort(key=len, reverse=True)
            self.uniq_commands[name[0]] = command
            for n in name:
                self.commands[n] = command

    def get_command(self, name):
        return self.commands.get(name, HelpClient)

    def display_help_message(self):
        for _, v in self.uniq_commands.items():
            obj = v if hasattr(v, '__dict__') else v()
            obj.describe_self()

    def execute(self):
        args = sys.argv[1:]
        main_command = args[0].replace('-', '') if args else 'help'
        if main_command == 'help':
            self.display_help_message()
        else:
            if main_command not in self.commands:
                print(f'{main_command} is not a valid command.')
                self.display_help_message()
                return
            class_or_object = self.get_command(main_command)
            obj = class_or_object if hasattr(
                class_or_object, '__dict__') else class_or_object()
            obj.run(args[1:])
