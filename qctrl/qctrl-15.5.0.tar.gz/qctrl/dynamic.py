# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Dynamically created classes."""
import inspect
import sys
from functools import wraps
from types import ModuleType
from typing import Callable


def dynamic_class(submodule: str) -> Callable:
    """Decorator to register a dynamic class. The decorated function should
    return the dynamic class to be registered.

    Parameters
    ----------
    submodule : str
        the submodule name that the class should be registered under
        e.g. `types`

    Returns
    -------
    Callable
        decorator for dynamic class
    """

    def customized_decorator(func: Callable):
        @wraps(func)
        def decorator(*args, **kwargs):
            cls = func(*args, **kwargs)
            register_dynamic_class(cls, submodule)
            return cls

        return decorator

    return customized_decorator


def register_dynamic_class(cls: type, submodule: str):
    """
    Registers the class to the given dynamic
    submodule.
    """
    assert inspect.isclass(cls)
    module_name = f"qctrl.dynamic.{submodule}"
    cls.__module__ = module_name
    cls.__package__ = module_name

    # module exists
    if module_name in sys.modules:
        module = sys.modules[module_name]

    # create new module
    else:
        module = ModuleType(module_name)
        sys.modules[module_name] = module

    setattr(module, cls.__name__, cls)


__all__ = ["dynamic_class", "register_dynamic_class"]
