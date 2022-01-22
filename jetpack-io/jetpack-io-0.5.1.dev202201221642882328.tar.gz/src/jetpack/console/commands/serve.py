import inspect

from cleo import application as cleo


class ServeCommand(cleo.Command):
    name = "serve"
    description = "Starts a server that exposes the module over the network"

    help = inspect.cleandoc(
        """
        <info>serve:</> Starts a server that exposes the module over the network

        The server is a grpc server that can be used to invoke functions and methods
        in the module.
        """
    )

    options = [
        cleo.Option(
            name="port",
            shortcut="p",
            description="Bind the network socket to this port",
        ),
    ]

    def handle(self) -> int:
        self.line_error("<error>serve: Not implemented yet.</>")
        return 0  # For now emulate success so we can write tests
