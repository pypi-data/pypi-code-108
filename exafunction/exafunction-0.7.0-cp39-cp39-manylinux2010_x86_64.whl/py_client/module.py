# Copyright Exafunction, Inc.

from typing import Dict

import exa._C as _C
from exa.common_pb.common_pb2 import MethodInfo
from exa.py_value.value import Value


class Module:
    """
    The Module class represents a remote module in the Exafunction system.

    Each remote module exposes one or more methods, which take in and return
    Exafunction values. Modules are created by Exafunction session, using the
    methods like Session.new_module.
    """

    def __init__(self, c: _C.Module):
        self._c = c

    def _check_valid(self):
        if not self._c.is_valid():
            raise ValueError("Module is not valid (was the session closed?)")

    def module_id(self) -> int:
        """
        Returns the module id.

        :return: The module id.
        """
        self._check_valid()
        return self._c.module_id()

    def run_method(self, method_name: str, **inputs: Value) -> Dict[str, Value]:
        """
        Runs a method on the remote module.

        :param method_name: The name of the method to run.
        :param inputs: The inputs to the method.
        :return: The outputs of the method.
        """
        self._check_valid()
        cc_inputs = {k: inp._c for k, inp in inputs.items()}
        cc_outputs = self._c.run_method(method_name, cc_inputs)
        return {k: Value(out) for k, out in cc_outputs.items()}

    def run(self, **inputs: Value) -> Dict[str, Value]:
        """
        Convenience method for running the method named "run" exposed by most modules.

        Equivalent to calling run_method with the method name "run".

        :param inputs: The inputs to the method.
        :return: The outputs of the method.
        """
        return self.run_method("run", **inputs)

    def ensure_local_valid(self, values: Dict[str, Value]):
        """
        Equivalent to calling ensure_local_valid on each value in the ValueMap
        to fetch its value. Using this function will generally reduce latency
        compared to fetching each value individually.

        :param values: The values to fetch.
        """

        self._check_valid()
        cc_values = {k: inp._c for k, inp in values.items()}
        self._c.ensure_local_valid(cc_values)

    def get_method_info(self, method_name: str = "run") -> MethodInfo:
        """
        Get information about a method, including its input and output types.

        If no method name is provided, the information for the "run" method
        is returned.

        :param method_name: The name of the method to get information about.
        :return: The method information.
        """
        self._check_valid()
        serialized_info = self._c.get_method_info(method_name)
        mi = MethodInfo()
        mi.ParseFromString(serialized_info)
        return mi
