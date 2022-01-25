import pytest

from whizbang.domain.menu.command_base import CommandBase, ICommandBase


class IRunTestsCommand(ICommandBase):
    """"""


class RunTestsCommand(CommandBase, IRunTestsCommand):

    @property
    def display_name(self) -> str:
        return 'run tests'

    @property
    def command_abbreviation(self) -> str:
        return 'r'

    @property
    def command_description(self) -> str:
        return 'run unit tests'

    def command(self):
        retcode = pytest.main(['tests/'])
