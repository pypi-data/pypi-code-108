"""Core module for generating a de-messaging backend module.

This module defines the base classes to serve a general python module as a
backend module in the Digital Earth messaging framework.

The most important members are:

.. autosummary::

    main
    BackendModule
    BackendFunction
    BackendClass
"""
from __future__ import annotations

from typing import Type

from demessaging.backend import utils  # noqa: F401
from demessaging.backend.class_ import BackendClass  # noqa: F401
from demessaging.backend.function import BackendFunction  # noqa: F401
from demessaging.backend.module import BackendModule
from demessaging.config import ModuleConfig


def main(
    module_name: str = "__main__", *args, **config_kws
) -> Type[BackendModule]:
    """Main function for starting a backend module from the command line."""
    from demessaging.cli import UNKNOWN_TOPIC, get_parser

    default_config: ModuleConfig

    if "config" in config_kws:
        default_config = config_kws.pop("config")
        default_config = default_config.copy(update=config_kws)
    else:
        config_kws.setdefault("topic", UNKNOWN_TOPIC)
        default_config = ModuleConfig(**config_kws)

    parser = get_parser(module_name, default_config)

    if args:
        ns = parser.parse_args(args)
    else:
        ns = parser.parse_args()

    ns_d = vars(ns)

    command = ns_d.pop("command", None)
    method_kws = {key: ns_d.pop(key) for key in ns_d.pop("command_params", [])}
    method_name = ns_d.pop("method_name", command)
    module_name = ns_d.pop("module_name")

    config = ModuleConfig(**ns_d)

    Model = BackendModule.create_model(module_name, config=config)

    if command:
        method = getattr(Model, method_name)
        print(method(**method_kws))

    return Model
