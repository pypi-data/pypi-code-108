from typing import Dict
from . import default
from . import junos_config


class ReturnValuesFactory:
    def __init__(self) -> None:
        """Create the appropriately-typed ReturnValues object, based on the Ansible
        module name. By default, will return the base class, ReturnValues.
        """
        self._constructors: Dict = {}
        self._default_constructor = default.ReturnValues

    def register(self, module_name, return_values_cls):
        """Register a ReturnValues extension Class to this Factory.

        Args:
            module_name (str): The particular Ansible Module that this ReturnValues is designed to process.
            return_values_cls (ReturnValues): A class that extends ReturnValues (i.e. and provides custom
            `pretty_diff` and `pretty_error` methods).

        Raises:
            ValueError: [description]
        """
        if module_name in self._constructors:
            raise ValueError(f"Conflicting module_name already registered: {self._constructors[module_name]}")
        if not issubclass(return_values_cls, self._default_constructor):
            raise ValueError(f"Must register a valid ReturnValues object that extends from {self._default_constructor}")
        self._constructors[module_name] = return_values_cls

    def build(self, return_values_raw, module_name):
        """Given raw Return Values from Ansible, parse them into a ReturnValues object.

        The caller can then use the `pretty_error` or `pretty_diff` methods on the returned object.

        Args:
            return_values_raw (Dict): The JSON data representing the Ansible Return Values
            module_name (str): The Ansible Module that produced these return values.

        Returns:
            ReturnValues: An object that provides `pretty_error` and `pretty_diff` methods.
        """
        try:
            return self._constructors[module_name](return_values_raw)
        except LookupError:
            return self._default_constructor(return_values_raw)


_factory = ReturnValuesFactory()
_factory.register('junos_config', junos_config.JunosConfigReturnValues)

def build(return_values_raw, module_name):
    return _factory.build(return_values_raw, module_name)
