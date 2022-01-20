import sys
from collections import namedtuple
from iosdebug.start import start
from iosdebug.stop import stop
from prompt_toolkit.shortcuts import button_dialog, input_dialog, message_dialog
import iosdebug.logger as logger
import webbrowser


Command = namedtuple("Command", "name, description, execute")

commands = [
    Command("start", "Stars debug mode", start),
    Command("stop", "Stops debug mode", stop),
    Command(
        "issue",
        "Creates an issue",
        lambda: webbrowser.open("https://github.com/tomnvt/ios-debug/issues/new"),
    ),
    Command("exit", "Exits execution", lambda: sys.exit()),
]


def get_selected_command():
    arguments = sys.argv
    if len(arguments) < 2:
        print("No command found. Please use one of the following:")
        _ = [print(command.name, "-", command.description) for command in commands]
        sys.exit(0)
    return arguments[1]


def try_command_execution(selected_command):
    command_names = [command.name for command in commands]
    if selected_command in command_names:
        print("Executing command:", selected_command)
        index = command_names.index(selected_command)
        commands[index].execute()
    else:
        print("No command found. Please use one of the following:")
        _ = [print(command.name, "-", command.description) for command in commands]


def main():
    if len(sys.argv) == 1:
        command_index = button_dialog(
            title="iOS Debug",
            text="Select an action:",
            buttons=[
                (command.name[0].upper() + command.name[1:], index)
                for index, command in enumerate(commands)
            ],
        ).run()

    else:
        command = sys.argv[1]
        command_names = [command.name for command in commands]
        try:
            command_index = command_names.index(command)
        except ValueError:
            print("Command not found.")
            print("Options:\n")
            _ = [print(name) for name in command_names]

    commands[command_index].execute()
    logger.delete_old_log_file()


if __name__ == "__main__":
    main()
