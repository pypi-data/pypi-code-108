from pathlib import Path
from typing import Union, Optional

from sandboxcreator.input_parser.sandbox import Sandbox
from sandboxcreator.vagrant_generator.vagrantfile import Vagrantfile
from sandboxcreator.ansible_generator.preconfig import Preconfig
from sandboxcreator.ansible_generator.provisioning import Provision

CSC_PATH: Path = Path(__file__).parent.resolve()
CONFIGURATION_PATH: Path = CSC_PATH.joinpath('resources/conf/configuration.yml')
FLAVORS_PATH: Path = CSC_PATH.joinpath('resources/conf/flavors.yml')


def _process_working_dir(working_dir: Optional[Union[str, Path]]) \
        -> Optional[Path]:
    """Validate and resolve working directory"""
    if working_dir is None:
        return None

    try:
        if isinstance(working_dir, str):
            working_directory: Path = Path(working_dir)
        elif isinstance(working_dir, Path):
            working_directory: Path = working_dir
        else:
            raise TypeError('Working directory has unknown type '
                            f'"{type(working_dir)}"')
        if not working_directory.is_absolute():
            raise ValueError('Working directory path '
                             f'"{str(working_directory)}" is not absolute')
        if not working_directory.exists():
            raise ValueError(f'Working directory "{str(working_directory)}" '
                             'does not exist')
        if not working_directory.is_dir():
            raise ValueError(f'Working directory "{str(working_directory)}" '
                             'is not a directory')
    except OSError:
        raise ValueError(f'Invalid path to working directory "{working_dir}"') \
            from None

    return working_directory


def _process_topology_path(topology: Union[str, Path],
                           working_dir: Optional[Path]) -> Path:
    """Validate and resolve topology path"""
    try:
        if isinstance(topology, str):
            topology_path: Path = Path(topology).resolve()
        elif isinstance(topology, Path):
            topology_path: Path = topology.resolve()
        else:
            raise TypeError('Topology definition file path has invalid type '
                            f'"{type(topology)}"')
        if working_dir is not None and not topology_path.is_absolute():
            topology_path = working_dir.joinpath(topology_path)
        if not topology_path.exists():
            raise ValueError(f'"{str(topology_path)}" does not exist')
        if not topology_path.is_file():
            raise ValueError(f'"{str(topology_path)}" is not a file')
    except OSError:
        raise ValueError(f'Invalid path to topology file "{topology}"') \
            from None

    return topology_path


def _process_output_path(output_dir: Optional[Union[str, Path]],
                         topology_path: Path,
                         working_dir: Optional[Path]) -> Path:
    """Validate and resolve output directory path"""
    try:
        if output_dir is None or output_dir == '':
            sandbox_path: Path = topology_path.parent.joinpath('sandbox')
        elif isinstance(output_dir, str):
            sandbox_path: Path = Path(output_dir).resolve()
        elif isinstance(output_dir, Path):
            sandbox_path: Path = output_dir.resolve()
        else:
            raise TypeError('Output directory path has invalid type '
                            f'"{type(output_dir)}"')
        if working_dir is not None and not sandbox_path.is_absolute():
            sandbox_path = working_dir.joinpath(sandbox_path)
        if sandbox_path.is_file():
            raise ValueError(f'Output directory "{sandbox_path}" is an existing'
                             ' file')
    except OSError:
        raise ValueError(f'Invalid output directory "{output_dir}"') from None

    return sandbox_path


def _process_provisioning_path(provisioning_dir: Optional[Union[str, Path]],
                               working_dir: Optional[Path]) -> Optional[Path]:
    """Validate and resolve user provisioning directory path"""
    try:
        if provisioning_dir is None or provisioning_dir == '':
            return None
        if isinstance(provisioning_dir, str):
            provisioning_path: Path = Path(provisioning_dir).resolve()
        elif isinstance(provisioning_dir, Path):
            provisioning_path: Path = provisioning_dir.resolve()
        else:
            raise TypeError('Provisioning directory path has invalid type '
                            f'"{type(provisioning_dir)}"')
        if working_dir is not None and not provisioning_path.is_absolute():
            provisioning_path = working_dir.joinpath(provisioning_path)
        if not provisioning_path.is_dir():
            raise ValueError(f'Directory "{provisioning_path}" does not exist')
        playbook_path: Path = provisioning_path.joinpath('playbook.yml')
        if not playbook_path.is_file():
            raise ValueError('Provisioning directory should contain '
                             '"playbook.yml" file')
    except OSError:
        raise ValueError('Invalid path to provisioning directory '
                         f'"{provisioning_dir}"') from None

    return provisioning_path


def _process_extra_vars_path(extra_vars: Optional[Union[str, Path]],
                             working_dir: Optional[Path]) -> Optional[Path]:
    """Validate and resolve path to Ansible extra vars file"""
    try:
        if extra_vars is None or extra_vars == '':
            return None
        if isinstance(extra_vars, str):
            extra_vars_path: Path = Path(extra_vars).resolve()
        elif isinstance(extra_vars, Path):
            extra_vars_path: Path = extra_vars.resolve()
        else:
            raise TypeError('Extra vars file path has invalid type '
                            f'"{type(extra_vars)}"')
        if working_dir is not None and not extra_vars_path.is_absolute():
            extra_vars_path = working_dir.joinpath(extra_vars_path)
        if not extra_vars_path.exists():
            raise ValueError(f'File "{str(extra_vars_path)}" does not exist')
        if extra_vars_path is not None and not extra_vars_path.is_file():
            raise ValueError(f'"{str(extra_vars_path)}" is not a file')
    except OSError:
        raise ValueError('Invalid path to extra variables file '
                         f'"{extra_vars}"') from None

    return extra_vars_path


def _generate_vagrantfile(sandbox_definition: Sandbox) -> None:
    """Initiate Vagrantfile generation"""

    vagrant_definition: Vagrantfile = Vagrantfile(sandbox_definition)
    vagrant_definition.generate(sandbox_definition.sandbox_dir /
                                'Vagrantfile', 'vagrantfile.j2')


def _generate_preconfig(sandbox_definition: Sandbox) -> None:
    """Initiate preconfig directory generation"""

    Preconfig.generate_preconfig(sandbox_definition)


def _generate_provisioning(sandbox_definition: Sandbox) -> None:
    """Initiate provisioning directory generation"""

    Provision.generate_user_provisioning(sandbox_definition)


def create(topology: Union[str, Path],
           output_dir: Optional[Union[str, Path]] = None,
           ansible_installed: bool = False,
           provisioning_dir: Optional[Union[str, Path]] = None,
           extra_vars: Optional[Union[str, Path]] = None,
           generate_provisioning: bool = False,
           verbose_ansible: bool = False,
           working_dir: Optional[Union[str, Path]] = None) -> None:
    """Generates intermediate definition from a topology definition.

    :param topology: path to the topology definition file
    :param output_dir: path to an output directory
    :param ansible_installed: whether the host machine have ansible installed
    :param provisioning_dir: path to directory with user provisioning files
    :param extra_vars: path to YAML file with additional values for Ansible
    :param generate_provisioning: whether provisioning should be regenerated
    :param verbose_ansible: whether Ansible output should be set to verbose
    :param working_dir: an absolute path to resolve possible relative paths
    """

    try:
        working_path: Optional[Path] = _process_working_dir(working_dir)
        topology_path: Path = _process_topology_path(topology, working_path)
        output_path: Path = _process_output_path(output_dir, topology_path,
                                                 working_path)
        provisioning_path: Path = _process_provisioning_path(provisioning_dir,
                                                             working_path)
        extra_vars_path: Path = _process_extra_vars_path(extra_vars,
                                                         working_path)
    except Exception as exception:
        raise RuntimeError(f'Could not process input variables:\n{exception}') \
            from None

    try:
        sandbox_definition: Sandbox = Sandbox(topology_path, CONFIGURATION_PATH,
                                              FLAVORS_PATH, output_path,
                                              ansible_installed,
                                              provisioning_path,
                                              extra_vars_path,
                                              generate_provisioning,
                                              verbose_ansible)
    except Exception as exception:
        raise RuntimeError(f'Definition parsing has failed:\n{exception}') \
            from None

    try:
        _generate_vagrantfile(sandbox_definition)
    except Exception as exception:
        raise RuntimeError(f'Could not generate Vagrantfile:\n{exception}') \
            from None

    try:
        _generate_preconfig(sandbox_definition)
        _generate_provisioning(sandbox_definition)
    except Exception as exception:
        raise RuntimeError('Could not generate provisioning files:\n'
                           f'{exception}') from None
