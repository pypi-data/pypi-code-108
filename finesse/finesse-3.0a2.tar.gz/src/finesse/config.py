"""Configuration tools."""

# NOTE: this module gets imported by `finesse` directly, so cannot itself import from
# `finesse` and cannot import packages that themselves import from `finesse`.
import os
from pathlib import Path
import importlib.resources
from configparser import RawConfigParser
import logging

from . import datastore
from .utilities import option_list

_PACKAGE_LOGGER = logging.getLogger(__package__)

show_progress_bars = False


def config_instance():
    """The Finesse configuration object for the current session.

    Returns
    -------
    :class:`configparser.RawConfigParser`
        The Finesse configuration object.
    """
    return datastore.init_singleton(_FinesseConfig)


def configure(plotting=False, jupyter_tracebacks=None, progress_bars=False):
    """Configure Finesse runtime options.

    Parameters
    ----------
    plotting : bool, optional
        Initialise Finesse plot theme for display.

    jupyter_tracebacks : bool, optional
        Show full tracebacks in Finesse errors when using Finesse in IPython. This
        setting does not work reliably in other environments.

    progress_bars : bool, optional
        When True progress bars will be displayed when available.

    See Also
    --------
    :func:`finesse.plotting.tools.init`
    """
    # NOTE: Before modifying this function, note that it may be called multiple times
    # during the execution of Finesse and should therefore remain idempotent.

    if plotting:
        from .plotting import init as init_plotting

        init_plotting(mode="display")

    if jupyter_tracebacks is not None:
        from .env import show_tracebacks

        show_tracebacks(jupyter_tracebacks)

    global show_progress_bars
    show_progress_bars = progress_bars


def autoconfigure():
    """Automatically configure runtime options based on the environment."""
    from .env import is_interactive

    kwargs = {}

    if is_interactive():
        # The user has imported Finesse inside a notebook or similar interactive
        # session. Configure some aspects of Finesse automatically: pretty plots and
        # suppress tracebacks.
        kwargs["plotting"] = False  # FIXME: docs don't build when True!
        kwargs["jupyter_tracebacks"] = False

    configure(**kwargs)


class _FinesseConfig(RawConfigParser):
    """The built-in and user configuration for Finesse.

    Do not instantiate this class directly; use :func:`config_instance`.
    """

    # Order in which user configs are loaded.
    _USER_CONFIG_LOAD_ORDER = ["user_config_path", "cwd_config_path"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.write_user_config()
        self._load_finesse_configs()

    @classmethod
    def user_config_paths(cls):
        return {
            config: getattr(cls, config)() for config in cls._USER_CONFIG_LOAD_ORDER
        }

    @classmethod
    def user_config_path(cls):
        return cls.user_config_dir() / "usr.ini"

    @classmethod
    def cwd_config_path(cls):
        return Path.cwd() / "finesse.ini"

    @classmethod
    def user_config_dir(cls):
        r"""The path to the user's config directory for Finesse.

        The exact path is determined by the current platform and the presence of certain
        environment variables:

        .. rubric:: Windows

        A folder called ``finesse`` in the folder pointed to by the environment variable
        ``%APPDATA`` (usually ``%HOMEPATH%\AppData\Roaming``).

        .. rubric:: POSIX (including Mac OS X and WSL)

        A directory called ``finesse`` inside either the path pointed to by the
        environment variable ``XDG_CONFIG_HOME`` or, if that value cannot be found or is
        empty, ``~/.config``.

        Returns
        -------
        :py:class:`pathlib.Path` or None
            The path to the Finesse config directory.

        Raises
        ------
        :py:class:`RuntimeError`
            If no config directory can be determined.
        """
        from .env import IS_WINDOWS

        if IS_WINDOWS:
            try:
                config_dir = Path(os.environ["APPDATA"])
            except KeyError:
                # NOTE: we assume %APPDATA% always exists on any normal Windows machine,
                # which should be the case. If it's not, we might need to change Finesse
                # to handle having no user config path.
                raise RuntimeError(
                    r"The %APPDATA% environment variable is required for Finesse to "
                    r"store user configuration, but it was not found. Please ensure "
                    r"this environment variable exists in the environment in which "
                    r"Finesse is being run."
                )
        else:
            # Path.home() raises RuntimeError if no home is found.
            config_dir = Path(
                os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
            )

        return config_dir / "finesse"

    @classmethod
    def write_user_config(cls, force=False):
        """Copy the default config files to the user's config directory."""
        logger = logging.getLogger(__name__)
        user_config_path = cls.user_config_path()

        if force or not user_config_path.is_file():
            # Copy barebone user config file contents into user's user config path.
            logger.info(f"Writing user config file to {user_config_path}.")

            user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with user_config_path.open("wb") as fobj:
                fobj.write(importlib.resources.read_binary(__package__, "usr.ini.dist"))

    def _load_finesse_configs(self):
        """Read the built-in and any user configuration files.

        The built-in configuration is loaded first, then the user configuration files
        are loaded in the order specified in :attr:`.USER_PATHS`. This means user
        configuration options can overwrite built-in options, and options from later
        paths in :attr:`.USER_PATHS` can overwrite options from earlier paths.
        """
        user_config_paths = self.user_config_paths().values()

        # Load the bundled configuration.
        self.read_string(
            importlib.resources.read_text(__package__, "finesse.ini"),
            source="<bundled finesse.ini>",
        )

        # Parse all configurations, from lowest to highest priority.
        parsed = self.read(user_config_paths)

        if not parsed:
            paths = option_list(user_config_paths)

            raise ConfigNotFoundError(f"Could not find user config files at {paths}.")


class ConfigNotFoundError(Exception):
    """Indicates a Finesse configuration could not be loaded."""
