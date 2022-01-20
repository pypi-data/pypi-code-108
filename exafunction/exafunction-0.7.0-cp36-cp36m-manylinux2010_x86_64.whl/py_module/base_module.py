# Copyright Exafunction, Inc.

import abc
from typing import Dict, Sequence

import exa._C as _C
from exa.common_pb.common_pb2 import ModuleConfiguration
from exa.common_pb.common_pb2 import ModuleInfo
from exa.common_pb.common_pb2 import ValueInfo
from exa.py_module.base_module_context import BaseModuleContext
from exa.py_module.base_module_context import wrap_call
from exa.py_module.method_context import MethodContext
from exa.py_value.value import Value


class BaseModule:
    def _initialize(self, ser_config: bytes) -> None:
        config = ModuleConfiguration()
        config.ParseFromString(ser_config)
        self.initialize(config.config_map)

    def initialize(self, config_map: Dict[str, bytes]) -> None:
        pass

    def module_info(self, module_ctx) -> ModuleInfo:
        info = ModuleInfo()
        for name, (inputs, outputs) in getattr(type(self), "_methods", {}).items():
            m = info.method_infos[name]
            for input_ in inputs:
                m.inputs[input_].SetInParent()
            for output in outputs:
                m.outputs[output].SetInParent()
        return info

    def _module_info(self, module_ctx: BaseModuleContext) -> str:
        info = self.module_info(module_ctx)
        return info.SerializeToString()

    def _run_method(
        self,
        ctx: MethodContext,
        method_name: str,
        inputs: Dict[str, _C.Value],
    ) -> Dict[str, _C.Value]:
        m = getattr(self, method_name)
        py_inputs = {k: Value(v) for k, v in inputs.items()}
        py_outputs = wrap_call(m, ctx, py_inputs)
        return {k: v._c for k, v in py_outputs.items()}


def export(inputs: Sequence[str], outputs: Sequence[str]):
    class ExportDecorator:
        def __init__(self, fn):
            self.fn = fn

        def __set_name__(self, owner, name):
            if not hasattr(owner, "_methods"):
                owner._methods = {}
            if name in owner._methods:
                raise ValueError(f"Already registered method {name} for export")
            owner._methods[name] = (tuple(inputs), tuple(outputs))
            setattr(owner, name, self.fn)

    return ExportDecorator
