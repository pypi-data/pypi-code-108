"""
description: this module provides the class ArgumentParser.
"""

import argparse
import textwrap
import colorama

SUPPRESS = argparse.SUPPRESS


class ArgumentParser(argparse.ArgumentParser):
    """
    this class inherits from argparse.ArgumentParser.

    this class can show the types and default values of parameters,
    automatically.
    """

    def __init__(self, *args, **kwargs):
        """
        this is the constructor of the class ArgumentParser.

        parameters:
            it will pass all import arguments into
            the function __init__ of class argparse.ArgumentParser.
        """

        super().__init__(*args, formatter_class=argparse.RawTextHelpFormatter, **kwargs)

    def add_argument(self, *argv, **kwargs):
        """
        override the function add_argument.
        it will format the help messages of argument.

        parameters:
            it will pass all import arguments into
            the function __init__ of class argparse.ArgumentParser.
        """

        if 'help' in kwargs and not kwargs['help'] == SUPPRESS:
            kwargs['help'] = kwargs['help'].strip().strip('.')
            comment_list = list()
            if 'type' in kwargs:
                comment_list.append(
                    '# parameter type: {type}'.format(
                        type=kwargs['type']))
            if 'default' in kwargs and not kwargs[
                                               'default'] == argparse.SUPPRESS:
                comment_list.append(
                    '# default value: {default}'.format(
                        default=kwargs['default']))

            comment = '' if len(comment_list) == 0 else (colorama.Fore.BLUE + '\n' + '\n'.join(comment_list) +
                                                         colorama.Fore.RESET)
            kwargs['help'] = '\n'.join(
                sum([textwrap.wrap(line) for line in
                     kwargs['help'].split('\n')], [])) + comment
        super().add_argument(*argv, **kwargs)
