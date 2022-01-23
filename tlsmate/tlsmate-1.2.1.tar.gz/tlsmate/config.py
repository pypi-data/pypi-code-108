# -*- coding: utf-8 -*-
"""Module containing the class for the configuration
"""
# import basic stuff
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, ItemsView, Union

# import own stuff
import tlsmate.structs as structs

# import other stuff
import configparser

config_logging = structs.ConfigItem("logging", type=str, default="error")
config_host = structs.ConfigItem("host", type=str, default="localhost")
config_port = structs.ConfigItem("port", type=int, default=443)
config_interval = structs.ConfigItem("interval", type=int, default=0)
config_key_log_file = structs.ConfigItem("key_log_file", type=str, default=None)
config_progress = structs.ConfigItem("progress", type=bool, default=False)
config_sni = structs.ConfigItem("sni", type=str, default=None)
config_ca_certs = structs.ConfigItem("ca_certs", type="file_list")
config_client_key = structs.ConfigItem("client_key", type="file_list")
config_client_chain = structs.ConfigItem("client_chain", type="file_list")
config_crl = structs.ConfigItem("crl", type=bool, default=True)
config_ocsp = structs.ConfigItem("ocsp", type=bool, default=True)
config_plugin = structs.ConfigItem("plugin", type="str_list", default=None)
config_recorder_delay = structs.ConfigItem("recorder_delay", type=bool, default=True)
config_proxy = structs.ConfigItem("proxy", type=str, default=None)
config_ipv6_preference = structs.ConfigItem("ipv6_preference", type=bool, default=False)


class Configuration(object):
    """Class representing the configuration for tlsmate.

    The configuration is taken from the following sources (the list is ordered
    according to the priority, first item has the least priority):

    * The hard coded default values
    * From the ini-file, if present. If the ini-file is not specified via the
      CLI option, the file .tlsmate.ini in the user's home directory will be used,
      if present.
    * Environment variables. They need to be given in upper cases and must start with
      `TLSMATE_` followed by the name of the setting in upper cases.
    * From the command line interface parameters

    Example:
        Specifying the logging option:

        Via command line::

            tlsmate --logging=debug ...

        Via Enviroment variable::

            export TLSMATE_LOGGING=debug

        Via ini-file::

            [tlsmate]
            logging = debug
    """

    def __init__(self) -> None:
        self._config_section: Optional[configparser.SectionProxy] = None
        self._config_section_read = False
        self._config: Dict[str, Any] = {}
        self._descr: Dict[str, structs.ConfigItem] = {}

        # register configurations which are essential in the core
        # part of tlsmate.
        for item in [
            config_logging,
            config_host,
            config_port,
            config_interval,
            config_key_log_file,
            config_progress,
            config_sni,
            config_ca_certs,
            config_client_key,
            config_client_chain,
            config_crl,
            config_ocsp,
            config_plugin,
            config_recorder_delay,
            config_proxy,
        ]:
            self.register(item)

    def _str_to_filelist(self, string):
        """Resolves a string of files paths.

        Multiple file paths are separated by a colon. If the path is a relative
        path, it is expanded to an absolute path, taking the directory of the
        config file as a base (which is available in self._config_dir).

        Arguments:
            string (str): the list of file paths as a string, multiple paths are
                separated by a colon.

        Returns:
            list of str: the list of resolved absolute paths.
        """

        ret = []
        for val in string.split(","):
            val = val.strip()
            if not val.startswith("/"):
                val = str(self._config_dir / val)
            ret.append(val)
        return ret

    _format_option = {
        bool: lambda self, x: x.lower() not in ["0", "off", "no", "false"],
        int: lambda self, x: int(x),
        "file_list": _str_to_filelist,
        "str_list": lambda self, x: [token.strip() for token in x.split(",")],
    }

    def _init_config_section(self, ini_file: Optional[Union[str, Path]]) -> None:
        if self._config_section_read:
            return

        self._config_section_read = True
        if ini_file is None:
            file_path = Path.home() / ".tlsmate.ini"
            if not file_path.is_file():
                return

        else:
            file_path = Path(ini_file)
            if not file_path.is_absolute():
                file_path = Path.cwd() / ini_file

            if not file_path.is_file():
                raise FileNotFoundError(ini_file)

        logging.debug(f"using config file {str(ini_file)}")
        self._config_dir = file_path.parent
        parser = configparser.ConfigParser()
        parser.read(str(file_path))
        if parser.has_section("tlsmate"):
            self._config_section = parser["tlsmate"]

    def _cast_item(self, item: str, val: Any) -> Any:
        """Cast the type of a configuration item into the internal format."""

        item_type = self._descr[item].type
        if item_type in self._format_option:
            val = self._format_option[item_type](self, val)
        return val

    def _determine_value(self, item: str) -> Any:
        val = os.environ.get("TLSMATE_" + item.upper())
        if val is None and self._config_section:
            val = self._config_section.get(item)  # type: ignore

        if val is not None:
            val = self._cast_item(item, val)

        return val

    def init_from_external(self, ini_file: Optional[Union[str, Path]] = None):
        """Take the configuration from the ini file and from the environment variables.

        Arguments:
            ini_file (str): the path to the ini file. If None is given, then only
                the environment variables are taken into account.
        """

        self._init_config_section(ini_file)
        for item in self._config:
            val = self._determine_value(item)
            if val is not None:
                self._config[item] = val

    def get_from_external(self, ini_file: Optional[str], item: str) -> Any:
        """Gets the value for a single itemerving the ini-file and the environment."""

        self._init_config_section(ini_file)
        return self._determine_value(item)

    def items(self) -> ItemsView[str, structs.ConfigItem]:
        """Return the configuration items. Mimics the dict's `items` method.

        Returns:
            The list of configuration items. Each item is a tuple of the item
            name and the item value.

        """

        return self._config.items()

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of a configuration item. Mimics the dict's `get` method.

        Arguments:
            key: the name of the configuration item
            default: the default value to return in case the configuration item is
                not existing. Defaults to None.

        Returns:
            the value of the configuration item or the provided default value if
            it is not present.
        """

        return self._config.get(key, default)

    def set(self, key: str, val: Any, keep_existing: bool = True) -> None:
        """Add a configuration option.

        Arguments:
            key: the name of the option
            val: the value of the option
            keep_existing: if set to True and the value is None, an existing
                configuration will not be overwritten. Defaults to True
        """

        if key in self._config and val is None and keep_existing:
            return

        self._config[key] = val

    def register(self, config_item: structs.ConfigItem) -> None:
        """Add a new item to the configuration

        Arguments:
            config_item: the configuration item to register

        Raises:
            ValueError: if a configuration item with the same name is already existing
        """

        name = config_item.name
        if name in self._descr:
            if config_item != self._descr[name]:
                raise ValueError(
                    f'configuration setting "{name}" already defined with '
                    f"different properties"
                )
        self._descr[name] = config_item
        self._config[name] = config_item.default
