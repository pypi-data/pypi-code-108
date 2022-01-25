# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import statsd  # type: ignore
import threading
from .. import Base
from ..config.parser import ApacheConfigParser, ConfigParserBase
from ..config.store import FileStore, RedisStore
from ..exceptions import ConfigurationConflict
from collections import namedtuple
from copy import copy
from redis import StrictRedis
from typing import Callable, Dict, Mapping, Optional, Type, cast

CONFIG_STORE_MAP: Mapping[str, Callable] = {
    "file": FileStore,
    "redis": RedisStore,
}
CONFIG_ARGUMENT_MAP: Mapping[str, Callable] = {"redis": StrictRedis}


def _parse_global_config(filename, config_parser: ConfigParserBase):
    """Parse config file with given config_parser.

    :param filename: filename
    :type filename: str
    :param config_parser: config parser to use
    :type config_parser: ConfigParserBase
    :return: config
    :rtype: dict
    """
    with open(filename, "r", encoding="utf-8") as config_file:
        content = config_file.read()

    return config_parser.parse(content)


class InfrastructureFactory(Base):
    """Infrastructure factory class.

    The infrastructure factory will create instances of registered
    "infrastructure" classes, with configuration for a specific context.
    """

    def __init__(
        self,
        config_file: str,
        config_parser: Optional[Type[ConfigParserBase]] = None,
    ):
        """Initialize an application service factory.

        After reading the configuration, it also configures the defaults
        in the statsd module.

        :param config_file: Global configuration file to read
        :type config_file: str
        :param config_parser: config parser used to parse global configuration
        :type config_parser: ConfigParserBase
        """
        self._local_storage = LocalInfrastructureStorage()
        if config_parser is None:
            config_parser = ApacheConfigParser

        self._config_parser = config_parser()

        self.logger.info(f"Using configuration file '{config_file}'")
        self._global_config = _parse_global_config(
            filename=config_file, config_parser=self._config_parser
        )

        config_store_type = self._global_config["InstanceConfig"]["type"]

        if config_store_type == "none":
            self._instance_config_store = None
        else:
            config_store_args = self._global_config["InstanceConfig"][
                "arguments"
            ]

            try:
                config_store_args = CONFIG_ARGUMENT_MAP[config_store_type](
                    **config_store_args
                )
            except KeyError:
                # There doesn't have to be an argument mapper
                pass

            config_store = CONFIG_STORE_MAP[config_store_type](
                parser=ApacheConfigParser(), arguments=config_store_args
            )

            self._instance_config_store = config_store

        if "statsd" in self._global_config:
            if "disabled" in self._global_config["statsd"]:
                self._global_config["statsd"]["disabled"] = bool(
                    int(self._global_config["statsd"]["disabled"])
                )
            statsd.Connection.set_defaults(**self._global_config["statsd"])
        else:
            # No statsd configuration available; forcefully disable it
            statsd.Connection.set_defaults(disabled=True)

        self._registered_infrastructure: Dict[str, Callable] = {}

    def __copy__(self):
        """Return a copy of the infrastructure factory.

        The copy will have a new (empty) infrastructure cache and registered
        infrastructure, but will share configuration with the original.
        """

        cls = self.__class__
        copy_factory = cls.__new__(cls)

        copy_factory._local_storage = LocalInfrastructureStorage()
        copy_factory._registered_infrastructure = copy(
            self._registered_infrastructure
        )

        copy_factory._config_parser = self._config_parser
        copy_factory._global_config = self._global_config
        copy_factory._instance_config_store = self._instance_config_store
        return copy_factory

    def get_config(self, context: str) -> dict:
        """Get config from infrafactory for given context.

        :param context: context
        :type context: str
        :return: config
        :rtype: dict
        """
        if self._instance_config_store is None or context is None:
            config = {**self._global_config}
        else:
            instance_config = self._instance_config_store.retrieve(context)
            config = {**self._global_config, **instance_config}
        return config

    def register_infrastructure(self, name: str, infrastructure: Callable):
        """Register an infrastructure class with the factory.

        :param cls: Class to register in the infrastructure factory
        :type cls: class
        """
        self._registered_infrastructure[name] = infrastructure

    def get_infrastructure(self, context: str, infrastructure_name: str):
        """Retrieve an infrastructure instance for the selected instance.

        If local_storage does not already have the infrastructure instance,
        it will be instantiated from infrastructure factory.

        :param infrastructure_name: Name of the infrastructure class to
            instantiate
        :type infrastructure_name: str
        :return: infrastructure
        :rtype: object
        """
        InfraKey = namedtuple("InfraKey", ["context", "infrastructure_name"])
        infra_key = InfraKey(
            context=context, infrastructure_name=infrastructure_name
        )
        try:
            return self._local_storage.infra[infra_key]
        except KeyError:
            pass

        try:
            infra = self.get_infra_from_infrastructure_factory(
                context=context, infrastructure_name=infrastructure_name
            )
        except KeyError as error:
            raise ConfigurationConflict(
                f"KeyError in infrastructure_factory.get_infrastructure: {error}"
            ) from error

        self._local_storage.infra[infra_key] = infra
        return infra

    def get_infra_from_infrastructure_factory(
        self, context: str, infrastructure_name: str
    ):
        """Retrieve an infrastructure instance for the selected instance.

        :param infrastructure_name: Name of the infrastructure class to
            instantiate
        :type infrastructure_name: str
        :return: infrastructure
        :rtype: object
        """
        config = self.get_config(context=context)

        timer = cast(
            statsd.Timer,
            self.statsd.get_timer(
                f"get_infrastructure,name={infrastructure_name}"
            ),
        )

        with timer.time():
            infra = self._registered_infrastructure[infrastructure_name](
                config=config
            )

        return infra

    def flush_local_storage(self):
        """Clean up all infrastructure in the local store.

        Usually called at the end of a request cycle. Some infrastructure
        instances might not have the `.clean_up(infrastructure)` method.
        """
        for infra_key, infra in self._local_storage.infra.items():
            timer = cast(
                statsd.Timer,
                self.statsd.get_timer(
                    f"cleanup,name={infra_key.infrastructure_name}"
                ),
            )

            with timer.time():
                try:
                    self._registered_infrastructure[
                        infra_key.infrastructure_name
                    ].clean_up(infra)
                except AttributeError:
                    # Infrastructure does not have clean_up method implemented.
                    pass
        self._local_storage.infra = {}
        return


class LocalInfrastructureStorage(threading.local):
    """Thread local storage for infrastructure."""

    def __init__(self):
        """Initialize the local storage for infrastructure with infra dict."""
        self.infra = {}
