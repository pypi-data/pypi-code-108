from whizbang.domain.menu.command_base import CommandBase, ICommandBase
from whizbang.domain.shared_types.named_solutions import NamedSolutions


class IListCommand(ICommandBase):
    """"""


class ListCommand(CommandBase, IListCommand):
    def __init__(self, named_solutions: NamedSolutions):
        super().__init__()
        self.solutions = named_solutions

    @property
    def display_name(self) -> str:
        return 'list'

    @property
    def command_abbreviation(self) -> str:
        return 'l'

    @property
    def command_description(self) -> str:
        return 'lists all solutions'

    @staticmethod
    def _variable_dir(obj):
        return [solution_field for solution_field in dir(obj) if not solution_field.startswith('__')]

    def command(self):
        list_of_commands = self._variable_dir(self.solutions)
        for i in list_of_commands:
            print(i)
