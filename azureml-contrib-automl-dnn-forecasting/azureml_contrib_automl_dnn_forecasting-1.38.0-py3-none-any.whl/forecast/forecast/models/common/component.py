"""Configs derived from `ModelComponentConfig` automatically persist their fully qualified name."""

from __future__ import annotations

import abc
import copy
import dataclasses as dc
import importlib


@dc.dataclass
class _ConfigType:
    module: str
    config_class: str


@dc.dataclass
class ModelComponentConfig(abc.ABC):
    """The base class from which all abstract component configs are derived.

    Attributes
    ----------
    config_type: _ConfigType
        A serializable form that specifies the config's class

    """

    config_type: _ConfigType = dc.field(init=False)

    def __post_init__(self) -> None:
        """Sets the attribute `config_type`.

        Returns
        -------
        None

        """
        c = self.__class__
        self.config_type = _ConfigType(module=c.__module__, config_class=c.__qualname__)

    @classmethod
    def fromdict(cls, d: dict) -> ModelComponentConfig:
        """Creates a config object from a `dict`.

        Parameters
        ----------
        d: dict
            A dictionary containing all information required to recreate a component's config.

        Returns
        -------
        ModelComponentConfig
            A concrete instance of a component config

        """
        key = 'config_type'
        if cls == cls.abstract_component_config():
            module = importlib.import_module(d[key]['module'])
            my_class = getattr(module, d[key]['config_class'])
        else:
            my_class = cls

        config = copy.deepcopy(d)
        if key in config:
            del config[key]
        return my_class(**config)

    @staticmethod
    @abc.abstractmethod
    def abstract_component_config() -> type:
        """Returns the component's abstract config class."""
        raise NotImplementedError()
