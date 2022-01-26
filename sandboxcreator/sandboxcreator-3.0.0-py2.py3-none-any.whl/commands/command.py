import abc
import csv
import subprocess
from enum import Enum
from pathlib import Path
from typing import List, Optional

from sandboxcreator.commands.command_attributes import CommandAttributes, \
    OutputLocation
from sandboxcreator.io.writer import Writer


class MachineState(Enum):
    """State of a virtual machine"""
    NOT_BUILT = 1
    RUNNING = 2
    NOT_RUNNING = 3
    SUSPENDED = 4

    def __str__(self):
        if self.name == "NOT_BUILT":
            return "not built"
        if self.name == "RUNNING":
            return "running"
        if self.name == "NOT_RUNNING":
            return "turned off"
        if self.name == "SUSPENDED":
            return "suspended"
        raise ValueError(f"Invalid machine state: {self.name}")


class Command(abc.ABC):
    """Abstract base class for all CSC commands"""

    @abc.abstractmethod
    def __init__(self, command_attributes: CommandAttributes):
        self._command_attributes: CommandAttributes = command_attributes

    @property
    @abc.abstractmethod
    def command_attributes(self) -> CommandAttributes:
        pass

    @command_attributes.setter
    @abc.abstractmethod
    def command_attributes(self, command_attributes: CommandAttributes) -> None:
        pass

    @abc.abstractmethod
    def execute(self) -> None:
        """Universal method for execution of the given command"""

    @staticmethod
    def translate_output_location(output_location: OutputLocation):
        """Translate Output enum values to subprocess values"""

        if output_location is OutputLocation.DEVNULL:
            return subprocess.DEVNULL
        if output_location is OutputLocation.STDOUT:
            return None
        raise ValueError('Invalid output device')

    @abc.abstractmethod
    def _check_machine_states(self) -> None:
        pass

    @staticmethod
    def list_machines(sandbox_dir: Path):
        status_command: List[str] = ["vagrant", "status", "--machine-readable"]
        try:
            process_output = subprocess.run(status_command, cwd=sandbox_dir,
                                            check=True, text=True,
                                            capture_output=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Could access list of machines") from None
        output_lines: List = process_output.stdout.splitlines()
        output_csv: List[List] = list(csv.reader(output_lines))
        machines: List[str] = []
        for line in output_csv:
            machine_name: str = line[1]
            if machine_name and machine_name not in machines:
                machines.append(machine_name)
        return machines

    @staticmethod
    def check_machine_state(vm_name: str,
                            sandbox_dir: Path) -> MachineState:
        status_command: List[str] = ["vagrant", "status", "--machine-readable",
                                     vm_name]
        try:
            process_output = subprocess.run(status_command, cwd=sandbox_dir,
                                            check=True, text=True,
                                            capture_output=True)
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Could not determine machine state - is the "
                               f'machine "{vm_name}" defined?') from None
        output_lines: List = process_output.stdout.splitlines()
        output_csv: List[List] = list(csv.reader(output_lines))
        if len(output_csv) >= 2 and "error" in output_csv[0]:
            if "Vagrant::Errors::MachineNotFound" in output_csv[1]:
                raise RuntimeError(f'Machine "{vm_name}" was not defined')
            raise RuntimeError(f"Vagrant error: {output_csv[1][3]}")

        state: str = ""
        for line in output_csv:
            if line[1] == vm_name and line[2] == "state":
                state = line[3]
                break
        if not state:
            raise ValueError(f'Could not check the state of "{vm_name}"')

        if state == "not_created":
            return MachineState.NOT_BUILT
        if state == "running":
            return MachineState.RUNNING
        if state == "saved":
            return MachineState.SUSPENDED
        if state == "poweroff":
            return MachineState.NOT_RUNNING

        raise ValueError(f'Unknown machine state "{state}"')


class BuildCommand(Command):
    """Build command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes) -> None:
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        self._command_attributes = command_attributes

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.RUNNING:
                raise RuntimeError(f'The machine "{machine}" is already running')
            if state is MachineState.SUSPENDED:
                raise RuntimeError(f'The machine "{machine}" is suspended - '
                                   'use the "resume" command to resume it')

    def _generate_cli_command(self) -> List[str]:
        if self.command_attributes.target_vm_names is None:
            return ["vagrant", "up"]
        return ["vagrant", "up"] + self.command_attributes.target_vm_names

    def _create_var_file(self) -> None:
        if not self.command_attributes.is_ansible_vars_set():
            return
        file_path: Path = self.command_attributes.\
            sandbox_path.joinpath("provisioning", "group_vars", "ansible.yml")
        Writer.generate_yaml(file_path, self.command_attributes.ansible_vars)

    def execute(self) -> None:
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        output_location: OutputLocation = self.command_attributes.cli_output_location
        error_location: OutputLocation = self.command_attributes.cli_error_location
        self._create_var_file()
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True,
                       stdout=Command.translate_output_location(output_location),
                       stderr=Command.translate_output_location(error_location))


class DestroyCommand(Command):
    """Destroy command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes):
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        if command_attributes.is_ansible_vars_set():
            raise AttributeError("ansible_vars is not a valid attribute of the "
                                 "command destroy")
        self._command_attributes = command_attributes

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.NOT_BUILT:
                raise RuntimeError(f'The machine "{machine}" is not built yet')

    def _generate_cli_command(self) -> List[str]:
        if self.command_attributes.target_vm_names is None:
            return ["vagrant", "destroy", "-f"]
        return ["vagrant", "destroy", "-f"] \
            + self.command_attributes.target_vm_names

    def _remove_var_file(self) -> None:
        var_file: Path = self.command_attributes.sandbox_path.\
            joinpath("provisioning", "group_vars", "ansible.yml")
        if var_file.is_file():
            Writer.remove_file(var_file)

    def execute(self) -> None:
        self._remove_var_file()
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        output_location: OutputLocation = self.command_attributes.cli_output_location
        error_location: OutputLocation = self.command_attributes.cli_error_location
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True,
                       stdout=Command.translate_output_location(output_location),
                       stderr=Command.translate_output_location(error_location))


class AccessCommand(Command):
    """Access command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes):
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        if command_attributes.target_vm_names is None:
            raise AttributeError("The target machine name is missing")
        if len(command_attributes.target_vm_names) != 1:
            raise AttributeError("You can access only one VM at a time")
        if command_attributes.is_ansible_vars_set():
            raise AttributeError("ansible_vars is not a valid attribute of the "
                                 "command access")
        self._command_attributes = command_attributes

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.NOT_BUILT:
                raise RuntimeError(f'The machine "{machine}" is not built yet -'
                                   'use the "build" command before accessing it')
            if state is MachineState.SUSPENDED:
                raise RuntimeError(f'The machine "{machine}" is suspended - use'
                                   ' the "resume" command before accessing it')
            if state is MachineState.NOT_RUNNING:
                raise RuntimeError(f'The machine "{machine}" is not running - '
                                   'use the "build" command before accessing it')

    def _generate_cli_command(self) -> List[str]:
        machines: List[str] = self.command_attributes.target_vm_names
        if machines is not None and isinstance(machines, List) and len(machines) == 1:
            return ["vagrant", "ssh"] + machines
        raise ValueError("One target VM name must be specified")

    def execute(self) -> None:
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True)


class SuspendCommand(Command):
    """Suspend command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes):
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        if command_attributes.is_ansible_vars_set():
            raise AttributeError("ansible_vars is not a valid attribute of the "
                                 "command suspend")
        self._command_attributes = command_attributes

    def _generate_cli_command(self) -> List[str]:
        if self.command_attributes.target_vm_names is None:
            return ["vagrant", "suspend"]
        return ["vagrant", "suspend"] + self.command_attributes.target_vm_names

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.NOT_BUILT:
                raise RuntimeError(f'The machine "{machine}" is not built yet')
            if state is MachineState.SUSPENDED:
                raise RuntimeError(f'The machine "{machine}" already suspended')
            if state is MachineState.NOT_RUNNING:
                raise RuntimeError(f'The machine "{machine}" is not running')

    def execute(self) -> None:
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        output_location: OutputLocation = self.command_attributes.cli_output_location
        error_location: OutputLocation = self.command_attributes.cli_error_location
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True,
                       stdout=Command.translate_output_location(output_location),
                       stderr=Command.translate_output_location(error_location))


class ResumeCommand(Command):
    """Resume command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes):
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        if command_attributes.is_ansible_vars_set():
            raise AttributeError("ansible_vars is not a valid attribute of the "
                                 "command resume")
        self._command_attributes = command_attributes

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.NOT_BUILT:
                raise RuntimeError(f'The machine "{machine}" is not built yet -'
                                   'use the "build" command to build it')
            if state is MachineState.RUNNING:
                raise RuntimeError(f'The machine "{machine}" is already running')
            if state is MachineState.NOT_RUNNING:
                raise RuntimeError(f'The machine "{machine}" is not running - '
                                   'use the "build" command to build it')

    def _generate_cli_command(self) -> List[str]:
        if self.command_attributes.target_vm_names is None:
            return ["vagrant", "resume"]
        return ["vagrant", "resume"] + self.command_attributes.target_vm_names

    def execute(self) -> None:
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        output_location: OutputLocation = self.command_attributes.cli_output_location
        error_location: OutputLocation = self.command_attributes.cli_error_location
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True,
                       stdout=Command.translate_output_location(output_location),
                       stderr=Command.translate_output_location(error_location))


class ShutdownCommand(Command):
    """Shutdown command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes):
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        if command_attributes.is_ansible_vars_set():
            raise AttributeError("ansible_vars is not a valid attribute of the "
                                 "command shutdown")
        self._command_attributes = command_attributes

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.NOT_BUILT:
                raise RuntimeError(f'The machine "{machine}" is not built yet')
            if state is MachineState.NOT_RUNNING:
                raise RuntimeError(f'The machine "{machine}" is not running')

    def _generate_cli_command(self) -> List[str]:
        if self.command_attributes.target_vm_names is None:
            return ["vagrant", "halt"]
        return ["vagrant", "halt"] + self.command_attributes.target_vm_names

    def execute(self) -> None:
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        output_location: OutputLocation = self.command_attributes.cli_output_location
        error_location: OutputLocation = self.command_attributes.cli_error_location
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True,
                       stdout=Command.translate_output_location(output_location),
                       stderr=Command.translate_output_location(error_location))


class ReloadCommand(Command):
    """Reload command"""

    def __init__(self, command_attributes: CommandAttributes):
        Command.__init__(self, command_attributes)

    @property
    def command_attributes(self) -> CommandAttributes:
        return self._command_attributes

    @command_attributes.setter
    def command_attributes(self, command_attributes):
        if not isinstance(command_attributes, CommandAttributes):
            raise TypeError("Command attributes must be an instance of "
                            "CommandAttributes")
        if command_attributes.is_ansible_vars_set():
            raise AttributeError("ansible_vars is not a valid attribute of the "
                                 "command reload")
        self._command_attributes = command_attributes

    def _check_machine_states(self) -> None:
        machines: Optional[List[str]] = self.command_attributes.target_vm_names
        sandbox_path: Path = self.command_attributes.sandbox_path
        if machines is None:
            machines = Command.list_machines(sandbox_path)
        for machine in machines:
            state: MachineState = Command.check_machine_state(machine,
                                                              sandbox_path)
            if state is MachineState.NOT_BUILT:
                raise RuntimeError(f'The machine "{machine}" is not built yet')
            if state is MachineState.SUSPENDED:
                raise RuntimeError(f'The machine "{machine}" is suspended - use'
                                   ' the "resume" command before reloading')
            if state is MachineState.NOT_RUNNING:
                raise RuntimeError(f'The machine "{machine}" is not running')

    def _generate_cli_command(self) -> List[str]:
        if self.command_attributes.target_vm_names is None:
            return ["vagrant", "reload"]
        return ["vagrant", "reload"] + self.command_attributes.target_vm_names

    def execute(self) -> None:
        self._check_machine_states()
        cli_command: List[str] = self._generate_cli_command()
        sandbox_location: Path = self.command_attributes.sandbox_path
        output_location: OutputLocation = self.command_attributes.cli_output_location
        error_location: OutputLocation = self.command_attributes.cli_error_location
        subprocess.run(cli_command,
                       cwd=sandbox_location,
                       check=True,
                       stdout=Command.translate_output_location(output_location),
                       stderr=Command.translate_output_location(error_location))
