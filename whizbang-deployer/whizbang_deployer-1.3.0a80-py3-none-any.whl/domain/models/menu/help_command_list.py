from whizbang.domain.menu.deploy_command import DeployCommand
from whizbang.domain.models.menu.command_list import CommandList
from whizbang.domain.menu.list_command import ListCommand
from whizbang.domain.menu.run_tests_command import RunTestsCommand


class HelpCommandList(CommandList):
    def __init__(self,
                 deploy_command: DeployCommand,
                 list_command: ListCommand,
                 run_tests_command: RunTestsCommand):
        CommandList.__init__(self,
                             deploy_command=deploy_command,
                             list_command=list_command,
                             run_tests_command=run_tests_command)
