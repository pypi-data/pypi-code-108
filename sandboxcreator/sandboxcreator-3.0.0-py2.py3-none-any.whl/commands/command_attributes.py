"""Objects related to command attributes"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union, Dict


class OutputLocation(Enum):
    """Manager output devices"""
    DEVNULL = 1
    STDOUT = 2


@dataclass
class CommandAttributes:
    """Dataclass for all command attributes"""

    def __init__(self, sandbox_path: Union[str, Path]):
        self._sandbox_path: Path = None
        self.sandbox_path = sandbox_path
        self._target_vm_names: Optional[List[str]] = None
        self._ansible_vars: Dict = {}
        self._cli_output_location: OutputLocation = OutputLocation.DEVNULL
        self._cli_error_location: OutputLocation = OutputLocation.STDOUT

    @property
    def sandbox_path(self) -> Path:
        """Return path to the sandbox"""
        return self._sandbox_path

    @sandbox_path.setter
    def sandbox_path(self, sandbox_path: Union[str, Path]) -> None:
        if isinstance(sandbox_path, Path):
            self._sandbox_path = sandbox_path.resolve()
        elif isinstance(sandbox_path, str):
            if not sandbox_path:
                raise ValueError('Sandbox path cannot be empty')
            self._sandbox_path = Path(sandbox_path).resolve()
        else:
            raise AttributeError("Path to sandbox must be a Path or a string")
        if not self.sandbox_path.is_dir():
            raise ValueError(f'Directory "{str(sandbox_path)}" does not exist')
        if not self.sandbox_path.joinpath('Vagrantfile').is_file():
            raise ValueError(f'Directory "{str(sandbox_path)}" does not '
                             f'contain Vagrantfile')

    @property
    def target_vm_names(self) -> Optional[List[str]]:
        """Return the list of target VM names or Null if empty"""
        return self._target_vm_names

    @target_vm_names.setter
    def target_vm_names(self, vm_names: Optional[List[str]]) -> None:
        if vm_names is None:
            self._target_vm_names = None
        elif isinstance(vm_names, list):
            if not vm_names:
                self._target_vm_names = None
            else:
                for vm_name in vm_names:
                    if not isinstance(vm_name, str):
                        raise AttributeError("VM names must be strings")
                self._target_vm_names = vm_names
        else:
            raise AttributeError("VM names must be None or a list of strings")

    def is_target_vm_names_set(self) -> bool:
        """Check if target_vm_names differs from default"""
        return self._target_vm_names is not None

    @property
    def ansible_vars(self) -> Dict:
        return self._ansible_vars

    @ansible_vars.setter
    def ansible_vars(self, ansible_variables: str) -> None:
        if not isinstance(ansible_variables, str):
            raise TypeError("Ansible values are expected in a string")
        if not ansible_variables:
            self._ansible_vars = {}
            return
        vs: List[List] = [x.split(":") for x in ansible_variables.split(';')]
        for variable in vs:
            if len(variable) == 2:
                self._ansible_vars.update({variable[0]: variable[1]})
            else:
                raise ValueError("Invalid format of Ansible variables")

    def is_ansible_vars_set(self) -> bool:
        return not self._ansible_vars == ""

    @property
    def cli_output_location(self) -> OutputLocation:
        """Return the location of the standard output of Vagrant and Ansible"""
        return self._cli_output_location

    @cli_output_location.setter
    def cli_output_location(self, output_location: OutputLocation) -> None:
        if isinstance(output_location, OutputLocation):
            self._cli_output_location = output_location
        else:
            raise AttributeError("Output location must be an instance of "
                                 "OutputLocation")

    def is_target_output_location_set(self) -> bool:
        """Check if location of the standard output differs from default"""
        return self._cli_output_location is not OutputLocation.DEVNULL

    @property
    def cli_error_location(self) -> OutputLocation:
        """Return the location of the error output of Vagrant and Ansible"""
        return self._cli_error_location

    @cli_error_location.setter
    def cli_error_location(self, error_location: OutputLocation) -> None:
        if isinstance(error_location, OutputLocation):
            self._cli_error_location = error_location
        else:
            raise AttributeError("Error location must be an instance of "
                                 "OutputLocation")

    def is_cli_error_location_set(self) -> bool:
        """Check if location of the error output differs from default"""
        return self._cli_error_location is not OutputLocation.DEVNULL
