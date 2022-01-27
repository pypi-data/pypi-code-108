import inspect

from cleo import application as cleo


class InvokeCommand(cleo.Command):
    name = "invoke"
    description = "Invokes a function in the current module"

    help = inspect.cleandoc(
        """
        <info>invoke:</> Invokes a function in the current module

        The function must have been exported via the jetpack SDK to be discoverable.
        <info>invoke</> is useful when trying to execute a function outside of an RPC call.
        For example, when launching the function as a job or cronjob.
        """
    )

    arguments = [
        cleo.Argument(
            name="symbol", description="The fully qualified name of the function"
        ),
        cleo.Argument(
            name="args",
            description="The arguments to be passed to the function as a base64 encoded string",
            required=False,  # So we can easily call functions that don't take args
        ),
    ]

    def handle(self) -> int:
        self.line_error("<error>invoke: Not implemented yet.</>")
        return 0  # For now emulate success so we can write tests
