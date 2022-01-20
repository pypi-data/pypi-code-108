"""Abstract Factory-like callables

To instantiate the right class given a configuration.

The factories are used throughout the entire package:
typically, different parts of the system do not need to know where to locate any other part.
"""
from importlib import import_module

from logzero import setup_logger

from .interfaces import (
    Configuration,
    ContainerBuilder,
    ContainerProvider,
    ContainerRunner,
    ContainerTech,
    DevContainer,
)

# A way to obtain 'devcontainers4all' dynamically
__NAMESPACE__ = __name__.split(".", maxsplit=1)[0]

# Factory names are CamelCase even if functions
# pylint: disable=invalid-name


def DevContainerFactory(config: Configuration) -> DevContainer:
    """Obtain the DevContainer implementation requested by configuration"""
    container_provider = ContainerProvider(config.devcontainer_provider)
    assert container_provider is ContainerProvider.VSC

    container_provider_module = import_module(
        f"{__NAMESPACE__}.providers.{container_provider.name.lower()}"
    )

    return container_provider_module.Manifest(config)


def ContainerRunnerFactory(config: Configuration) -> ContainerRunner:
    """Obtain the DevContainer implementation requested by configuration"""
    container_tech = ContainerTech(config.container_tech)
    assert container_tech is ContainerTech.DOCKER

    container_tech_module = import_module(
        f"{__NAMESPACE__}.technologies.{container_tech.name.lower()}"
    )

    return container_tech_module.Runner(config=config)


def ContainerBuilderFactory(config: Configuration) -> ContainerBuilder:
    """Obtain the ContainerBuilder implementation requested by configuration"""
    container_tech = ContainerTech(config.container_tech)
    assert container_tech is ContainerTech.DOCKER

    container_tech_module = import_module(
        f"{__NAMESPACE__}.technologies.{container_tech.name.lower()}"
    )

    return container_tech_module.Builder(config=config)


class Controller:
    """Control the process

    A technology and provider agnostic controller
    """

    def __init__(self, configuration: Configuration) -> None:
        self.__config = configuration
        self.__logger = setup_logger(name=self.__class__.__name__)

    def shell(self) -> int:
        """Open a shell againt the devcontainer

        Dependin on configuration, this implies also (re-)creating the containarised image before creating a container
        against it and opening a shell
        """
        image_name = self.create()

        runner = ContainerRunnerFactory(config=self.__config)
        self.__logger.info("Executing %s in container", image_name)

        return runner.run(image_id=image_name)

    def create(self):
        """Create the containarised image"""
        devcontainer = DevContainerFactory(self.__config)
        builder = ContainerBuilderFactory(self.__config)

        args = devcontainer.get("build").get("args")
        image_name = builder.build(buildargs=args)

        self.__logger.info("Image %s created", image_name)

        return image_name
