from figcli.commands.factory import Factory
from figcli.commands.figgy_context import FiggyContext
from figcli.commands.help.configure import Configure
from figcli.commands.help.login import Login
from figcli.commands.help_context import HelpContext
from figcli.config import *
from figcli.svcs.setup import FiggySetup
from figcli.utils.utils import Utils, CollectionUtils


class HelpFactory(Factory):
    def __init__(self, command: CliCommand, context: HelpContext, figgy_context: FiggyContext):
        self._command = command
        self._context = context
        self._figgy_context = figgy_context
        self._options = context.options
        self._utils = Utils(False)
        self._setup: FiggySetup = FiggySetup(self._figgy_context)

    def instance(self):
        return self.get(self._command)

    def get(self, command: CliCommand):
        if configure in self._options:
            return Configure(self._context, self._setup)
        elif command == login or command == sandbox:
            return Login(self._context, self._setup, self._figgy_context)
        else:
            self._utils.error_exit(f"{command.name} is not a valid command. You must select from: "
                                   f"[{CollectionUtils.printable_set(help_commands)}]. Try using --help for more info.")
