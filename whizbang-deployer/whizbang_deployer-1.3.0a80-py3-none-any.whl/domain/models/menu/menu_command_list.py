from whizbang.domain.menu.deploy_command import DeployCommand
from whizbang.domain.menu.run_tests_command import RunTestsCommand
from whizbang.domain.menu.help_command import HelpCommand
from whizbang.domain.menu.list_command import ListCommand
from whizbang.domain.models.menu.command_list import CommandList


class MenuCommandList(CommandList):
    def __init__(self,
                 help_command: HelpCommand,
                 deploy_command: DeployCommand,
                 list_command: ListCommand,
                 run_tests_command: RunTestsCommand):
        CommandList.__init__(self,
                             deploy_command=deploy_command,
                             list_command=list_command,
                             run_tests_command=run_tests_command)
        self.command_list.append(help_command)

