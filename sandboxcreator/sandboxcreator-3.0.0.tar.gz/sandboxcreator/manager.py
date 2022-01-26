from pathlib import Path
from typing import Optional, Union, List

import sandboxcreator.commands.command as commands
from sandboxcreator.commands.command_attributes import CommandAttributes, OutputLocation


def _create_command(command_name: str,
                    command_attributes: Optional[CommandAttributes]) -> commands.Command:
    """Create a Command object from the command name"""
    if not isinstance(command_name, str):
        raise TypeError("Command name must be a string")
    if not isinstance(command_attributes, CommandAttributes):
        raise TypeError("Command attributes must be an instance of "
                        "CommandAttributes")
    if command_name == "build":
        return commands.BuildCommand(command_attributes)
    if command_name == "destroy":
        return commands.DestroyCommand(command_attributes)
    if command_name == "access":
        return commands.AccessCommand(command_attributes)
    if command_name == "suspend":
        return commands.SuspendCommand(command_attributes)
    if command_name == "resume":
        return commands.ResumeCommand(command_attributes)
    if command_name == "shutdown":
        return commands.ShutdownCommand(command_attributes)
    if command_name == "reload":
        return commands.ReloadCommand(command_attributes)
    raise AttributeError(f'Unknown command: {command_name}')


def manage(command_name: str,
           sandbox_location: Union[str, Path],
           machines: Optional[List[str]] = None,
           ansible_vars: str = "",
           output: OutputLocation = OutputLocation.DEVNULL,
           error: OutputLocation = OutputLocation.DEVNULL) -> None:
    """Vagrant wrapper to simplify sandbox instantiation and manipulation.

    :param command_name: name of the command to execute
    :param sandbox_location: path to the sandbox directory
    :param machines: list of involved machine names
    :param ansible_vars: variables for Ansible
    :param output: where to dump the command line output
    :param error: where to dump the command line error output
    """

    try:
        command_args: CommandAttributes = CommandAttributes(sandbox_location)
        command_args.target_vm_names = machines
        command_args.cli_output_location = output
        command_args.ansible_vars = ansible_vars
        command_args.cli_error_location = error
        command: commands.Command = _create_command(command_name, command_args)
    except Exception as e:
        raise RuntimeError(f"Could not prepare command for execution:\n{e}")
    try:
        command.execute()
    except Exception as e:
        raise RuntimeError(f"Could not execute command:\n{e}")
