from whizbang.domain.solution.solution_factory import ISolutionFactory
from whizbang.domain.menu.command_base import CommandBase, ICommandBase


class IDeployCommand(ICommandBase):
    """"""


class DeployCommand(CommandBase, IDeployCommand):
    def __init__(self, solution_factory: ISolutionFactory):
        self.__solution_factory = solution_factory

    @property
    def display_name(self) -> str:
        return 'deploy'

    @property
    def command_abbreviation(self) -> str:
        return 'd'

    @property
    def command_description(self) -> str:
        return 'deploy a solution by name'

    def command(self):
        if self._solution_name is None:
            self._solution_name = input('enter solution name:  ')
        # try:
        solution = self.__solution_factory.get_solution(self._solution_name)
        solution.deploy()
        # except AttributeError:
        #     print(f'Whizbang does not recognize the solution {solution_name}.')
