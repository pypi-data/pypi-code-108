from typing import Optional

from qm.pb.inc_qua_pb2 import QuaProgram
from qm.program.StatementsCollection import StatementsCollection
from qm.program._ResultAnalysis import _ResultAnalysis


class _Program:
    def __init__(self, config=None, program: Optional[QuaProgram] = None):
        super().__init__()
        self._program = program if program is not None else QuaProgram()
        self._program.script.SetInParent()
        self._program.resultAnalysis.SetInParent()
        self._program.script.body.SetInParent()
        self._qua_config = config
        self._result_analysis = _ResultAnalysis(self._program.resultAnalysis)
        self._is_in_scope = False

    def _declare_var(self, name, var_type, size, value, dim, is_input_stream):
        declaration = self._program.script.variables.add()
        declaration.name = name
        declaration.type = var_type
        declaration.size = size
        declaration.dim = dim
        declaration.isInputStream = is_input_stream
        if value is None:
            pass
        elif type(value) is list:
            for i in value:
                added_value = declaration.value.add()
                added_value.CopyFrom(i)
        else:
            added_value = declaration.value.add()
            added_value.CopyFrom(value)

    def declare_int(self, name, size, value, dim, is_input_stream):
        self._declare_var(name, QuaProgram.INT, size, value, dim, is_input_stream)

    def declare_real(self, name, size, value, dim, is_input_stream):
        self._declare_var(name, QuaProgram.REAL, size, value, dim, is_input_stream)

    def declare_bool(self, name, size, value, dim, is_input_stream):
        self._declare_var(name, QuaProgram.BOOL, size, value, dim, is_input_stream)

    @property
    def body(self):
        return StatementsCollection(self._program.script.body)

    @property
    def result_analysis(self) -> _ResultAnalysis:
        return self._result_analysis

    def build(self, config):
        copy = QuaProgram()
        copy.CopyFrom(self._program)
        copy.config.CopyFrom(config)
        return copy

    def set_in_scope(self):
        self._is_in_scope = True

    def set_exit_scope(self):
        self._is_in_scope = False

    def is_in_scope(self) -> bool:
        return self._is_in_scope
