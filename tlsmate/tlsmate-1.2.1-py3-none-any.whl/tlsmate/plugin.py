# -*- coding: utf-8 -*-
"""Module providing stuff for plugin handling
"""
# import basic stuff
import logging
import abc
import sys
import argparse
from typing import List, Optional, Type, Any

# import own stuff
import tlsmate.config as conf
import tlsmate.structs as structs

# import other stuff


class Args(object):
    """Helper class to simplify specification of argparse arguments.

    Arguments:
        args: one optional argument
        kwargs: any number of named arguments
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.arg = args[0] if args else None
        self.kwargs = kwargs


class Plugin(metaclass=abc.ABCMeta):
    """Base class for plugins

    A plugin can be:

        - a subcommand
        - an argument group
        - a single argument

    A plugin may have:

        - an associated configuration item
        - a list of plugins which are plugged in into this class
        - a list of workers, which by default will be registered if

            - the plugin is a subcommand or
            - the associated configuration is not False and not None

    The default plugin behavior can be overruled by specific class methods.

    Attributes:
        config: an optional associated configuration item
        group: parameters for the add_argument_group method (argparse)
        subcommand: parameters for the add_subparsers method
        cli_args: parameters for the add_argument method (argparse)
        plugins: A list of plugin classes which are plugged in into this
            plugin.
        workers: a list of worker classes to be registered
    """

    config: Optional[structs.ConfigItem] = None
    group: Optional[Args] = None
    subcommand: Optional[Args] = None
    cli_args: Optional[Args] = None
    plugins: Optional[List[Type["Plugin"]]] = None
    workers: Optional[List[Type["Worker"]]] = None

    @classmethod
    def args_name(cls) -> str:
        """Helper method to retrieve the args-attribute from the attribute arguments.

        Returns:
            the attribute name for the args object
        """

        assert cls.cli_args
        if "dest" in cls.cli_args.kwargs:
            return cls.cli_args.kwargs["dest"]

        name = cls.cli_args.arg
        if name.startswith("--"):
            name = name[2:]

        return name.replace("-", "_")

    @classmethod
    def extend(cls, plugin: Type["Plugin"]) -> Type["Plugin"]:
        """Decorator to extend a plugin
        """

        if cls.plugins is None:
            cls.plugins = []

        cls.plugins.append(plugin)
        return plugin

    @classmethod
    def extend_parser(cls, parser: argparse.ArgumentParser, subparsers: Any) -> None:
        """Extends the parser (subcommand, argument group, or argument)

        Arguments:
            parser: the CLI parser object
            subparsers: the subparser object
        """

        if cls.cli_args:
            parser.add_argument(cls.cli_args.arg, **cls.cli_args.kwargs)

        elif cls.subcommand and subparsers:
            parser = subparsers.add_parser(cls.subcommand.arg, **cls.subcommand.kwargs)

        elif cls.group:
            parser = parser.add_argument_group(**cls.group.kwargs)  # type: ignore

        if cls.plugins is not None:
            for plugin in cls.plugins:
                plugin.extend_parser(parser, subparsers)

    @classmethod
    def register_config(cls, config: conf.Configuration) -> None:
        """Registers its configuration item, if defined.

        Arguments:
            config: The configuration object.
        """

        if cls.config:
            config.register(cls.config)

        if cls.plugins:
            for plugin in cls.plugins:
                plugin.register_config(config)

    @classmethod
    def args_parsed(
        cls,
        args: Any,
        parser: argparse.ArgumentParser,
        subcommand: str,
        config: conf.Configuration,
    ) -> None:
        """Callback after the arguments are parsed.

        Provides the configuration (based on the argument) and registers the workers.

        Arguments:
            args: the parsed arguments object
            parser: the CLI parser object
            subcommand: the subcommand that was given
            config: The configuration object.
        """

        if cls.subcommand and cls.subcommand.arg != subcommand:
            return

        register_workers = False
        if cls.cli_args and cls.config:
            val = getattr(args, cls.args_name())
            if val is not None:
                config.set(cls.config.name, val)

        if cls.config:
            register_workers = config.get(cls.config.name) not in [None, False]

        elif cls.subcommand:
            register_workers = True

        if register_workers and cls.workers is not None:
            for worker in cls.workers:
                WorkManager.register(worker)

        if cls.plugins is not None:
            for plugin in cls.plugins:
                plugin.args_parsed(args, parser, subcommand, config)


class ArgPlugin(Plugin):
    """Plugin for specifying the plugins that shall be loaded.
    """

    config = conf.config_plugin
    cli_args = Args(
        "--plugin",
        nargs="*",
        type=str,
        help=(
            "list of plugins to load. The name of each plugin must start with "
            "`tlsmate_`."
        ),
    )


class ArgConfig(Plugin):
    """Plugin for the config file argument.
    """

    cli_args = Args(
        "--config",
        dest="config_file",
        default=None,
        help="ini-file to read the configuration from.",
    )


class ArgLogging(Plugin):
    """Plugin for the logging argument.
    """

    cli_args = Args(
        "--logging",
        choices=["critical", "error", "warning", "info", "debug"],
        help="sets the logging level. Default is error.",
        default="error",
    )


class BaseCommand(Plugin):
    """The base class for tlsmate. To be extended by plugins.
    """

    plugins = [ArgPlugin, ArgConfig, ArgLogging]

    @classmethod
    def create_parser(cls):
        parser = argparse.ArgumentParser(
            description=(
                "tlsmate is an application for testing and analyzing TLS servers. "
                "Test scenarios can be defined in a simple way with great flexibility. "
                "A TLS server configuration and vulnerability scan is built in."
            )
        )
        subparsers = parser.add_subparsers(title="commands", dest="subcommand")
        cls.extend_parser(parser, subparsers)
        return parser

    @classmethod
    def args_parsed(cls, args, parser, subcommand, config):
        if args.subcommand is None:
            parser.error("Subcommand is mandatory")
        super().args_parsed(args, parser, args.subcommand, config)


class Worker(metaclass=abc.ABCMeta):
    """Provides a base class for the implementation of a worker.

    Attributes:
        name (str): name of the worker, used for logging purposes only
        prio (int): all workers are executed according to their the priority.
            A lower value indicates higher priority, i.e., the worker with the lowest
            value will run first. If two workers have the same priority, their
            execution order will be determined by the alphabetical order of their
            name attribute.
        server_profile (:obj:`tlsmate.server_profile.ServerProfile`): The server
            profile instance. Can be used to get data from it (e.g. which cipher
            suites are supported for which TLS versions), or to extend it.
        client (:obj:`tlsmate.client.Client`): The client object.
        config (:obj:`tlsmate.config.Configuration`): The configuration object.
    """

    prio = 100

    def __init__(self, tlsmate):
        self._tlsmate = tlsmate
        self.server_profile = tlsmate.server_profile
        self.client = tlsmate.client
        self.config = tlsmate.config

    @abc.abstractmethod
    def run(self):
        """Entry point for the worker.

        The work manager will call this method which actually let worker do its job.
        """

        raise NotImplementedError


class WorkManager(object):
    """Manages the registered workers and runs them.

    The worker manager provides an interface to register workers.

    The registered workers are triggered based on their priority by calling their
    run method.
    """

    _instance = None

    def __init__(self):
        WorkManager._instance = self
        self._prio_pool = {}

    def _register(self, worker_class):
        self._prio_pool.setdefault(worker_class.prio, [])
        self._prio_pool[worker_class.prio].append(worker_class)

    @classmethod
    def register(cls, worker_class):
        """Register a worker plugin class.

        Can be used as a decorator.

        Arguments:
            worker_class (:class:`Worker`): A worker class to be registered.

        Returns:
            :class:`Worker`: the worker class passed as argument
        """

        cls._instance._register(worker_class)
        return worker_class

    def run(self, tlsmate):
        """Function to actually start the work manager.

        The run method of all registered worker plugins will be called according to the
        priority of the workers.

        Arguments:
            tlsmate (:obj:`tlsmate.tlsmate.TlsMate`): The tlsmate object which is passed
                to the run methods of the workers.
        """

        for prio_list in sorted(self._prio_pool.keys()):
            for cls in sorted(self._prio_pool[prio_list], key=lambda cls: cls.name):
                if tlsmate.config.get("progress"):
                    sys.stderr.write(f"\n{cls.descr}")
                    sys.stderr.flush()

                logging.debug(f"starting worker {cls.name}")
                cls(tlsmate).run()
                logging.debug(f"worker {cls.name} finished")
