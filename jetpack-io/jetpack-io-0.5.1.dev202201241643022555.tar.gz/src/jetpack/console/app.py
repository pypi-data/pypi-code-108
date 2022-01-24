from typing import List, cast

from cleo import application as cleo

from jetpack.console.commands.invoke import InvokeCommand
from jetpack.console.commands.serve import ServeCommand


class CommandLineApp(cleo.Application):
    def __init__(self) -> None:
        # For now using "module" as the application name, but if there's a way
        # to get a way to pass in the name set by an end-user we could pass that
        # instead.
        # Similarly, we could pass in the tag of the docker container as a version.
        super().__init__("module", "0.1")

        # Default commands:
        commands = [
            InvokeCommand(),
            ServeCommand(),
        ]

        for command in commands:
            self.add(command)

    def run(self) -> int:
        exit_code: int = super().run()
        return exit_code


def main() -> int:
    return CommandLineApp().run()
