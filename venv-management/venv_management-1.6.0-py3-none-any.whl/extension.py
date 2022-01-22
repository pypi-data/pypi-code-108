"""The plug-in extension mechanism.
"""

import inspect
from abc import ABC, abstractmethod
from pathlib import Path

import pkg_resources
import stevedore
import stevedore.exception


class ExtensionError(Exception):
    """Raised if there is an error in an extension."""
    pass


def list_extensions(namespace):
    """List the names of the extensions available in a given namespace."""
    extensions = stevedore.ExtensionManager(
        namespace=namespace,
        invoke_on_load=False,
    )
    return extensions.names()


def list_dirpaths(namespace):
    """A mapping of extension names to extension package paths."""
    extensions = stevedore.ExtensionManager(
        namespace=namespace,
        invoke_on_load=False,
    )
    return {name: _extension_dirpath(ext) for name, ext in extensions.items()}


def _extension_dirpath(ext: stevedore.extension.Extension) -> Path:
    """Get the directory path to an extension package.

    Args:
        ext: A stevedore.extension.Extension instance.

    Returns:
        A absolute Path to the package containing the extension.
    """
    return Path(pkg_resources.resource_filename(ext.module_name, ""))


class Extension(ABC):
    """A generic extension point for plug-ins."""

    def __init__(self, name):
        self._name = name

    @property
    def kind(self) -> str:
        """The kind of extension."""
        return self._kind()

    @abstractmethod
    def _kind(self):
        raise NotImplementedError

    @property
    def name(self) -> str:
        """The name of the extension.

        The is the same as the name used to create the extension.
        """
        return self._name

    @classmethod
    def dirpath(cls):
        """The directory path to the extension package."""
        package_name = inspect.getmodule(cls).__package__
        return pkg_resources.resource_filename(package_name, "")

    @property
    def version(self):
        """The version of the extension."""
        return "1.0.0"  # We allow extensions to have a distinct version but don't exploit this yet


def create_extension(kind, namespace, name, exception_type, *args, **kwargs) -> Extension:
    """Create an instance of a named extension.

    Args:
        kind: The kind of extension to create.
        namespace: The namespace within which the extension is a member.
        name: The name of the extension.
        exception_type: The type of exception to be raised if an extension could not be created.
        *args: Positional arguments to forward to the extensions constructor.
        **kwargs: Keyword arguments to forward to the extensions constructor.

    Returns:
        An extension instance.

    Raises:
        exception_type: If the requested extension could not be located.
    """
    try:
        manager = stevedore.driver.DriverManager(
            namespace=namespace,
            name=name,
            invoke_on_load=True,
            invoke_args=args,
            invoke_kwds={**kwargs, "name": name},
        )
    except stevedore.exception.NoMatches as no_matches:
        names = list_extensions(namespace)
        name_list = ", ".join(names)
        raise exception_type(
            f"No {kind} matching {name !r}. Available {kind}s: {name_list}"
        ) from no_matches
    driver = manager.driver
    return driver
