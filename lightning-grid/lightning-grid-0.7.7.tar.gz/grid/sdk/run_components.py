import typing
from dataclasses import dataclass, field


@dataclass
class ScratchSpace:
    """Represents compute node hard drives mounted in an experiment to be used as scratch space.

    Parameters
    ----------
    size_gb
        Size of the hard disk to mount in GB.
    mount_path
        Path to where the hard disk should be mounted.
    """
    size_gb: int = 100
    mount_path: str = '/scratch'


@dataclass
class Resources:
    """Represents compute node hard drives mounted in an experiment to be used as scratch space.

    Parameters
    ----------
    instance_type
        Instance type to use to launch the experiment
    use_spot
        If ``True``, inturuptable instance types will be used to launch the
        experiment computations. This trades the potential of longer
        times to completion for drastically reduced prices.
    cpus
        Number of CPUs to use per exeriment. If more CPUs are requested than
        exist on the compute node, the experiment will run with the total
        number of cpus which are available on a machine type. If zero (the
        default) then use all cpus available on a machine.
    gpus
        Number of GPUs to use per exeriment (requires an instance type
        to be selected which contains GPUs). If more GPUs are requested than
        exist on the compute node, the experiment will run with the total
        number of gpus which are available on a machine type. If zero (the
        default) then use all gpus available on a machine.
    storage_gb
        Size of the hard disk (GB) used to mount the root of the experiment
        file system. Must be >= 100 GB.
    extra
        Additional selectors to use to request machines. Not for general use
        unless instructed to by the grid team as part of your support contract.
    """
    instance_type: str = 't2.medium'
    use_spot: bool = False
    cpus: int = 0
    gpus: int = 0
    storage_gb: int = 100
    extra: typing.Dict[str, str] = field(default_factory=dict)


@dataclass
class Actions:
    """Actions define commands executed at specific points in the run lifecycle.

    Actions are able to influence experiment image generation
    before building source code, after building source code,
    before starting the user program, or after the user program ends.

    Parameters
    ----------
    on_build
        commands to add as RUN instructions. These instructions are
        executed before any dependencies are installed. Note: this
        cannot be set if using custom Dockerfile
    on_build_start
        commands passed to the image builder which are interpreted
        as RUN commands in a Dockerfile. Executes before installing
        dependencies from package manager.
    on_build_end
        commands passed to the image builder which are interpreted
        as RUN commands in a Dockerfile. Executes after installing
        dependencies from package manager.
    on_experiment_start
        allows users to specify commands that need to be executed
        sequentially before the main experiment process starts.
        This command will be executed on every experiment that the
        run creates.
    on_experiment_end
        allows users to specify commands that need to be executed
        sequentially after the main experiment process ends. This
        command will be executed on every experiment that the run
        creates.
    """
    on_build: typing.List[str] = None
    on_build_start: typing.List[str] = None
    on_build_end: typing.List[str] = None
    on_experiment_start: typing.List[str] = None
    on_experiment_end: typing.List[str] = None
