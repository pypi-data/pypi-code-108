from benvy.databricks.notebook.CommandConverter import CommandConverter


class CommandsConverter:
    def __init__(self, command_converter: CommandConverter):
        self.__command_converter = command_converter

    def convert(self, commands: list, first_line: str, cell_separator: str) -> str:
        while commands[len(commands) - 1]["command"] == "":
            commands.pop()

        commands.sort(key=lambda command: command["position"])
        commands = [command for command in commands if command["subtype"] == "command"]
        commands = list(map(self.__command_converter.convert, commands))

        output = f"\n\n{cell_separator}\n\n".join(commands)

        return self._format(first_line, output)

    def _format(self, first_line: str, output: str):
        if output[-1:] != "\n":
            output += "\n"

        return first_line + "\n" + output
