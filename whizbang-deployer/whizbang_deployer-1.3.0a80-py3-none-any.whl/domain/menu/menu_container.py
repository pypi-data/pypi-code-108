
from dependency_injector import containers, providers

from whizbang.domain.menu.deploy_command import DeployCommand
from whizbang.domain.menu.help_command import HelpCommand
from whizbang.domain.menu.list_command import ListCommand
from whizbang.domain.menu.menu_invoker import MenuInvoker
from whizbang.domain.menu.run_tests_command import RunTestsCommand
from whizbang.domain.models.menu.help_command_list import HelpCommandList
from whizbang.domain.models.menu.menu_command_list import MenuCommandList
from whizbang.domain.shared_types.named_solutions import NamedSolutions


class MenuContainer(containers.DeclarativeContainer):
    solution_factory = providers.Dependency()

    named_solutions = providers.Factory(
        NamedSolutions
    )

    list_command = providers.Factory(
        ListCommand,
        named_solutions=named_solutions
    )

    deploy_command = providers.Factory(
        DeployCommand,
        solution_factory=solution_factory
    )

    run_tests_command = providers.Factory(
        RunTestsCommand
    )

    help_command_list = providers.Factory(
        HelpCommandList,
        deploy_command=deploy_command,
        list_command=list_command,
        run_tests_command=run_tests_command
    )

    help_command = providers.Factory(
        HelpCommand,
        help_command_list=help_command_list
    )

    menu_command_list = providers.Factory(
        MenuCommandList,
        deploy_command=deploy_command,
        list_command=list_command,
        run_tests_command=run_tests_command,
        help_command=help_command
    )

    menu_invoker = providers.Singleton(
        MenuInvoker,
        menu_command_list=menu_command_list
    )

