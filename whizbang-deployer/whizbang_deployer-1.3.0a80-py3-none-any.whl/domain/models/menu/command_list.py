from whizbang.domain.menu.deploy_command import DeployCommand
from whizbang.domain.menu.list_command import ListCommand
from whizbang.domain.menu.run_tests_command import RunTestsCommand
from whizbang.domain.menu.command_base import CommandBase


class CommandList:
    def __init__(self,
                 deploy_command: DeployCommand,
                 list_command: ListCommand,
                 run_tests_command: RunTestsCommand):
        self.command_list: 'list[CommandBase]' = []
        self.command_list.append(deploy_command)
        self.command_list.append(list_command)
        self.command_list.append(run_tests_command)