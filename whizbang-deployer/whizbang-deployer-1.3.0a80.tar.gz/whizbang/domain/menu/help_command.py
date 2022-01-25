from whizbang.domain.menu.command_base import CommandBase, ICommandBase
from whizbang.domain.models.menu.help_command_list import HelpCommandList


class IHelpCommand(ICommandBase):
    """"""


class HelpCommand(CommandBase):
    def __init__(self, help_command_list: HelpCommandList):
        super().__init__()
        self._help_command_list = help_command_list.command_list

    @property
    def display_name(self) -> str:
        return 'help'

    @property
    def command_abbreviation(self) -> str:
        return 'h'

    @property
    def command_description(self) -> str:
        return 'help'

    def __build_help_list(self):
        help_list = []
        for command in self._help_command_list:
            help_list.append(f'{command.display_name} - {command.command_description}')
        return help_list

    def command(self):
        help_list = self.__build_help_list()
        for command in help_list:
            print(command)
