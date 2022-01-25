from time import sleep
from typing import List

from whizbang.domain.menu.command_base import ICommandBase

import logging
_log = logging.getLogger(__name__) 


class CommandMenu(object):
    """FIXME:  This whole system should probably be replaced with a first class package, like FASTCLI."""
    
    def __init__(self, options: List[ICommandBase] = None, title=None, refresh=lambda: None):
        self.options = options
        self.title = title
        self.is_title_enabled = self.title
        self.refresh = self.set_refresh(refresh=refresh)
        self.is_open = None

    CLOSE = 'close'

    @staticmethod
    def set_refresh(refresh):
        if not callable(refresh):
            raise TypeError(refresh, "refresh is not a function")
        return refresh

    def open_menu(self):
        self.is_open = True
        while self.is_open:
            print()
            self.refresh()
            command = self.enter()
            if command == CommandMenu.CLOSE:
                command = self.close_menu
            if command is not None:
                print()
                command()

    def close_menu(self):
        self.is_open = False

    def display(self):
        if self.is_title_enabled:
            self.is_title_enabled = False
            print(self.title)
            print()
            sleep(1.5)
        for option in self.options:
            print(option.display_name)
        print(CommandMenu.CLOSE)
        print()

    def enter(self):
        if len(self.options) == 0:
            return CommandMenu.CLOSE
        self.display()
        user_input = input()
        if user_input == 'close' or user_input == 'c':
            return CommandMenu.CLOSE
        for option in self.options:
            if option.display_name == user_input or option.command_abbreviation == user_input:
                option.command()
                return
        print(f'The command: {user_input} is not a valid command')
