#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

from typing import Iterable
from rich.console import Console


def print_help_with_spaces(text):
    print('  ' + text)


class AosKeysError(Exception):
    def __init__(self, message, help_text=None):
        super().__init__(message)
        self.help_text = help_text

    def print_message(self):
        console = Console()
        console.print(f'ERROR: {str(self)}', style='red')

        if not self.help_text:
            return

        if not isinstance(self.help_text, Iterable):
            print_help_with_spaces(self.help_text)

        for row in self.help_text:
            print_help_with_spaces(row)
