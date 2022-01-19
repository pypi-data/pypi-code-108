from typing import Optional

from qm.ExpressionSerializingVisitor import ExpressionSerializingVisitor
from qm.QuaNodeVisitor import QuaNodeVisitor
from qm.pb.inc_qua_pb2 import QuaProgram


class QuaSerializingVisitor(QuaNodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._indent = 0
        self._lines = []
        self.tags = []

    def out(self):
        return "\n".join(["from qm.qua import *", ""] + self._lines + [""])

    def _out_lines(self):
        return self._lines

    def _default_enter(self, node) -> bool:
        name = node.DESCRIPTOR.full_name
        statement = _statements.get(name, None)
        block = _blocks.get(name, None)
        if name not in _dont_print:
            print(f"entering {name}")
        if statement:
            self._line(statement(node))
        if block:
            self._enter_block(block(node))
        return statement is None

    def enter_qm_grpc_qua_QuaResultAnalysis(self, node) -> bool:
        if len(node.ListFields()) > 0:
            self._enter_block("with stream_processing():")
            return True
        else:
            return False

    def enter_qm_grpc_qua_QuaProgram_SaveStatement(self, node):
        if node.tag not in self.tags:
            self._line(f"{node.tag} = declare_stream()")
            self.tags.append(node.tag)
        saveLine = (
            f"save({ExpressionSerializingVisitor.serialize(node.source)}, {node.tag})"
        )
        self._line(saveLine)
        return False

    def enter_qm_grpc_qua_QuaProgram_VarDeclaration(self, node):
        args = self._get_declare_var_args(node)

        if node.isInputStream:
            self._line(
                f"{node.name} = declare_input_stream({_var_type_dec[node.type]}, {_dict_to_python_call(args)})"
            )
        else:
            self._line(
                f"{node.name} = declare({_var_type_dec[node.type]}, {_dict_to_python_call(args)})"
            )

        return False

    def _get_declare_var_args(self, node):
        size = node.size
        dim = node.dim
        args = {}
        if dim > 0:
            args["size"] = size
        if dim > 0 and len(node.value) > 0:
            args["value"] = "[" + ", ".join([_ser_exp(it) for it in node.value]) + "]"
        elif len(node.value) == 1:
            args["value"] = _ser_exp(node.value[0])
        if "value" in args and "size" in args:
            del args["size"]
        return args

    def enter_qm_grpc_qua_QuaProgram_MeasureStatement(self, node):
        if node.streamAs and node.streamAs not in self.tags:
            self._line(f"{node.streamAs} = declare_stream()")
            self.tags.append(node.streamAs)
        return self._default_enter(node)

    def visit_qm_grpc_qua_QuaProgram_ForStatement(self, node):
        super()._default_visit(node.body)

    def visit_qm_grpc_qua_QuaProgram_ForEachStatement(self, node):
        super()._default_visit(node.body)

    def visit_qm_grpc_qua_QuaProgram_IfStatement(self, node):
        super()._default_visit(node.body)
        elseifs_list = node.elseifs
        for elseif in elseifs_list:
            elseif_block = elseif.body
            condition = elseif.condition
            if len(elseif_block.statements) > 0:
                self._leave_block()
                self._line(
                    f"with elif_({ExpressionSerializingVisitor.serialize(condition)}):"
                )
                self._enter_block()
                super()._default_visit(elseif_block)

        else_block = getattr(node, "else")
        if len(else_block.statements) > 0:
            self._leave_block()
            self._line("with else_():")
            self._enter_block()
            super()._default_visit(else_block)

    def visit_qm_grpc_qua_QuaProgram_PlayStatement(self, node):
        pulse_one_of = node.WhichOneof("pulseType")
        if pulse_one_of == "namedPulse":
            pulse = f'"{node.namedPulse.name}"'
            # node.pulse - duplicate with namedPulse
        elif pulse_one_of == "rampPulse":
            pulse = f"ramp({ExpressionSerializingVisitor.serialize(node.rampPulse)})"

        element = node.qe.name
        amp = ""
        v0 = _ser_exp(node.amp.v0)
        v1 = _ser_exp(node.amp.v1)
        v2 = _ser_exp(node.amp.v2)
        v3 = _ser_exp(node.amp.v3)
        if v0 != "":
            if v1 != "":
                amp = f"*amp({v0}, {v1}, {v2}, {v3})"
            else:
                amp = f"*amp({v0})"
        args = []
        if len(node.duration.ListFields()) == 1:
            _, value = node.duration.ListFields()[0]
            args.append(f"duration={_ser_exp(value)}")
        if len(node.condition.ListFields()) == 1:
            _, value = node.condition.ListFields()[0]
            args.append(f"condition={_ser_exp(value)}")
        if node.targetInput:
            args.append(f'target="{node.targetInput}"')
        if len(node.chirp.ListFields()) > 0:
            rate_one_of = node.chirp.WhichOneof("rate")
            if rate_one_of == "scalarRate":
                rate = ExpressionSerializingVisitor.serialize(node.chirp.scalarRate)
            elif rate_one_of == "arrayRate":
                rate = ExpressionSerializingVisitor.serialize(node.chirp.arrayRate)

            sunits = node.chirp.units
            if sunits == node.chirp.HzPerNanoSec:
                units = "Hz/nsec"
            elif sunits == node.chirp.mHzPerNanoSec:
                units = "mHz/nsec"
            elif sunits == node.chirp.uHzPerNanoSec:
                units = "uHz/nsec"
            elif sunits == node.chirp.nHzPerNanoSec:
                units = "nHz/nsec"
            elif sunits == node.chirp.pHzPerNanoSec:
                units = "pHz/nsec"
            else:
                raise Exception("Unsupported units " + sunits)

            timesBuilder = []
            for time in node.chirp.times:
                timesBuilder.append(f"{time}")

            if len(timesBuilder) > 0:
                times = f'[{", ".join(timesBuilder)}]'
            else:
                times = "None"

            args.append(f'chirp=({rate},{times},"{units}")')
        if len(node.truncate.ListFields()) == 1:
            _, value = node.truncate.ListFields()[0]
            args.append(f"truncate={_ser_exp(value)}")

        # TODO maybe make sure no other fields?

        if len(args) > 0:
            args_str = f', {", ".join(args)}'
        else:
            args_str = ""
        self._line(f'play({pulse}{amp}, "{element}"{args_str})')

    def _default_leave(self, node):
        name = node.DESCRIPTOR.full_name
        block = _blocks.get(name, None)
        if block is not None:
            self._leave_block()
        super()._default_leave(node)

    def _enter_block(self, line: Optional[str] = None):
        if line is not None:
            self._line(line)
        self._indent += 1

    def _leave_block(self):
        self._indent -= 1

    def _line(self, line: str):
        self._lines.append((self._indent * "    ") + line)


def _ser_exp(value):
    return ExpressionSerializingVisitor.serialize(value)


def _dict_to_python_call(d: dict) -> str:
    return ", ".join([f"{k}={v}" for k, v in d.items()])


def _ramp_to_zero_statement(node):
    args = []
    args.append(f'"{node.qe.name}"')
    if len(node.duration.ListFields()) == 1:
        args.append(f"{node.duration.value}")
    return f'ramp_to_zero({", ".join(args)})'


def _measure_statement(node):
    args = []
    args.append(f'"{node.pulse.name}"')
    args.append(f'"{node.qe.name}"')
    if node.streamAs:
        args.append(f"{node.streamAs}")
    else:
        args.append(f"None")
    if len(node.measureProcesses) > 0:
        for process in node.measureProcesses:
            args.append(ExpressionSerializingVisitor.serialize(process))
    return f'measure({", ".join(args)})'


def _wait_statement(node):
    args = []
    if len(node.time.ListFields()) == 1:
        _, value = node.time.ListFields()[0]
        args.append(f"{ExpressionSerializingVisitor.serialize(value)}")
    qes = []
    for qe in node.qe:
        qes.append(f'"{qe.name}"')
    args.append(", ".join(qes))
    return f'wait({", ".join(args)})'


def _align_statement(node):
    args = []
    for qe in node.qe:
        args.append(f'"{qe.name}"')
    return f'align({", ".join(args)})'


def _wait_for_trigger_statement(node):
    args = []
    for qe in node.qe:
        args.append(f'"{qe.name}"')
    if node.pulseToPlay.name:
        args.append(f'"{node.pulseToPlay.name}"')
    return f'wait_for_trigger({", ".join(args)})'


def _frame_rotation_statement(node):
    args = []
    args.append(f"{ExpressionSerializingVisitor.serialize(node.value)}")
    args.append(f'"{node.qe.name}"')
    return f'frame_rotation_2pi({", ".join(args)})'


def _reset_frame_statement(node):
    args = []
    args.append(f'"{node.qe.name}"')
    return f'reset_frame({", ".join(args)})'


def _update_frequency_statement(node):
    args = []
    args.append(f'"{node.qe.name}"')
    args.append(f"{ExpressionSerializingVisitor.serialize(node.value)}")
    if node.units == QuaProgram.UpdateFrequencyStatement.Hz:
        args.append(f'"Hz"')
    elif node.units == QuaProgram.UpdateFrequencyStatement.mHz:
        args.append(f'"mHz"')
    elif node.units == QuaProgram.UpdateFrequencyStatement.uHz:
        args.append(f'"uHz"')
    elif node.units == QuaProgram.UpdateFrequencyStatement.nHz:
        args.append(f'"nHz"')
    elif node.units == QuaProgram.UpdateFrequencyStatement.pHz:
        args.append(f'"pHz"')
    else:
        raise RuntimeError(f'unknown units "{node.units}"')
    args.append(f"{node.keepPhase}")
    return f'update_frequency({", ".join(args)})'


def _set_dc_offset_statement(node):
    args = []
    args.append(f'"{node.qe.name}"')
    args.append(f'"{node.qeInputReference}"')
    args.append(f"{ExpressionSerializingVisitor.serialize(node.offset)}")
    return f'set_dc_offset({", ".join(args)})'


def _advance_input_stream_statement(node):
    if node.streamArray.name != "":
        input_stream = ExpressionSerializingVisitor.serialize(node.streamArray)
    elif node.streamVariable.name != "":
        input_stream = ExpressionSerializingVisitor.serialize(node.streamVariable)
    else:
        raise RuntimeError("unsupported type for pop input stream")
    return f"advance_input_stream({input_stream})"


def _for_block_statement(node):
    condition = ExpressionSerializingVisitor.serialize(node.condition)
    if len(node.init.statements) == 0 and len(node.update.statements) == 0:
        if condition == "True":
            return f"with infinite_loop_():"
        else:
            return f"with while_({condition}):"
    else:
        if len(node.init.statements) != 1:
            raise Exception("for is not valid")
        if len(node.update.statements) != 1:
            raise Exception("for is not valid")

        init = node.init.statements[0].assign
        update = node.update.statements[0].assign

        if init is None:
            raise Exception("for is not valid")
        if update is None:
            raise Exception("for is not valid")

        return f"with for_({ExpressionSerializingVisitor.serialize(init.target)},{ExpressionSerializingVisitor.serialize(init.expression)},{condition},{ExpressionSerializingVisitor.serialize(update.expression)}):"


def _for_each_block_statement(node):
    variables = []
    arrays = []
    for it in node.iterator:
        variables.append(_ser_exp(it.variable))
        arrays.append(it.array.name)
    return f'with for_each_(({",".join(variables)}),({",".join(arrays)})):'


def _if_block_statement(node):
    condition = ExpressionSerializingVisitor.serialize(node.condition)
    return f"with if_({condition}):"


def _stream_processing_function(array):
    function = array[0].string_value

    if function == "average":
        return f"average()"

    if function == "dot":
        if len(array) == 1:
            return f"tuple_dot_product()"
        else:
            vector = _stream_processing_operator(array[1].list_value.values)
            return f"dot_product({vector})"

    if function == "vmult":
        vector = _stream_processing_operator(array[1].list_value.values)
        return f"multiply_by({vector})"

    if function == "smult":
        return f"multiply_by({array[1].string_value})"

    if function == "tmult":
        return f"tuple_multiply()"

    if function == "conv":
        if len(array) == 2:
            if array[1].string_value:
                mode = f'"{array[1].string_value}"'
            else:
                mode = ""
            return f"tuple_convolution({mode})"
        else:
            vector = _stream_processing_operator(array[2].list_value.values)
            if array[1].string_value:
                mode = f',"{array[1].string_value}"'
            else:
                mode = ""
            return f"convolution({vector}{mode})"

    if function == "fft":
        return f"fft()"

    if function == "booleancast":
        return f"boolean_to_int()"

    if function == "demod":
        if len(array[2].list_value) > 0:
            cos = _stream_processing_operator(array[2].list_value.values)
        else:
            cos = array[2].string_value
        if len(array[3].list_value) > 0:
            sin = _stream_processing_operator(array[3].list_value.values)
        else:
            sin = array[3].string_value
        return f"demod({array[1].string_value},{cos},{sin})"

    print(f"missing function: {function}")
    return f"default_function()"


def _stream_processing_operator(array):
    operator = array[0].string_value

    if operator == "@macro_input":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.input{array[1].string_value}()"

    if operator == "@array":
        values = []
        for a in array[1:]:
            if len(a.list_value) > 0:
                value = _stream_processing_operator(a.list_value.values)
            else:
                value = a.string_value
            values.append(value)
        return f'[{", ".join(values)}]'

    if operator == "@macro_auto_reshape":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.auto_reshape()"

    if operator == "+":
        left = _stream_processing_statement(array[1])
        right = _stream_processing_statement(array[2])
        return f"{left}.add({right})"  # arithmetic stream

    if operator == "-":
        left = _stream_processing_statement(array[1])
        right = _stream_processing_statement(array[2])
        return f"{left}.subtract({right})"  # arithmetic stream

    if operator == "/":
        left = _stream_processing_statement(array[1])
        right = _stream_processing_statement(array[2])
        return f"{left}.divide({right})"  # arithmetic stream

    if operator == "*":
        left = _stream_processing_statement(array[1])
        right = _stream_processing_statement(array[2])
        return f"{left}.multiply({right})"  # arithmetic stream

    if operator == "zip":
        left = _stream_processing_statement(array[1])
        right = _stream_processing_statement(array[2])
        return f"{right}.zip({left})"  # arithmetic stream

    if operator == "take":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.take({array[1].string_value})"

    if operator == "buffer":
        chain = _default_stream_processing_chain(array)
        dims = [dim.string_value for dim in array[1:-1]]
        return f'{chain}.buffer({", ".join(dims)})'

    if operator == "bufferAndSkip":
        chain = _default_stream_processing_chain(array)
        return (
            f"{chain}.buffer_and_skip({array[1].string_value}, {array[2].string_value})"
        )

    if operator == "skip":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.skip({array[1].string_value})"

    if operator == "skipLast":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.skip_last({array[1].string_value})"

    if operator == "histogram":
        chain = _default_stream_processing_chain(array)
        bins = _stream_processing_operator(array[1].list_value.values)
        return f"{chain}.histogram({bins})"

    if operator == "average":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.average()"

    if operator == "flatten":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.flatten()"

    if operator == "map":
        chain = _default_stream_processing_chain(array)
        return f"{chain}.map(FUNCTIONS.{_stream_processing_function(array[1].list_value.values)})"

    if operator == "@re":
        chain = _default_stream_processing_chain(array)
        timestamp_mode = int(array[1].string_value)
        if timestamp_mode == 0:  # values
            return f"{chain}"
        elif timestamp_mode == 1:  # timestamps
            return f"{chain}.timestamps()"
        elif timestamp_mode == 2:  # ValuesAndTimestamps
            return f"{chain}.with_timestamps()"

    print(f"missing operator: {operator}")
    chain = _default_stream_processing_chain(array)
    return f"{chain}"


def _default_stream_processing_chain(array):
    lastIndex = len(array) - 1
    chain = _stream_processing_statement(array[lastIndex])
    return f"{chain}"


def _stream_processing_statement(node):
    if len(node.list_value) > 0:
        return _stream_processing_operator(node.list_value.values)
    else:
        return node.string_value


def _stream_processing_terminal_statement(node):
    lastIndex = len(node.values) - 1
    chain = _stream_processing_statement(node.values[lastIndex])
    terminal = node.values[0].string_value
    terminal = "save_all" if terminal == "saveAll" else terminal  # normalize save all
    return f'{chain}.{terminal}("{node.values[1].string_value}")'


def _serialize(node):
    visitor = QuaSerializingVisitor()
    visitor.visit(node)
    return visitor._out_lines()


_blocks = {
    "qm.grpc.qua.QuaProgram": lambda n: "with program() as prog:",
    "qm.grpc.qua.QuaProgram.ForStatement": _for_block_statement,
    "qm.grpc.qua.QuaProgram.ForEachStatement": _for_each_block_statement,
    "qm.grpc.qua.QuaProgram.IfStatement": _if_block_statement,
}

_statements = {
    "qm.grpc.qua.QuaProgram.MeasureStatement": _measure_statement,
    "qm.grpc.qua.QuaProgram.WaitStatement": _wait_statement,
    "qm.grpc.qua.QuaProgram.AssignmentStatement": lambda n: f"assign({ExpressionSerializingVisitor.serialize(n.target)}, "
    f"{ExpressionSerializingVisitor.serialize(n.expression)})",
    "qm.grpc.qua.QuaProgram.PauseStatement": lambda n: "pause()",
    "qm.grpc.qua.QuaProgram.ResetPhaseStatement": lambda n: f'reset_phase("{n.qe.name}")',
    "qm.grpc.qua.QuaProgram.UpdateFrequencyStatement": _update_frequency_statement,
    "qm.grpc.qua.QuaProgram.AlignStatement": _align_statement,
    "qm.grpc.qua.QuaProgram.WaitForTriggerStatement": _wait_for_trigger_statement,
    "qm.grpc.qua.QuaProgram.ZRotationStatement": _frame_rotation_statement,
    "qm.grpc.qua.QuaProgram.RampToZeroStatement": _ramp_to_zero_statement,
    "qm.grpc.qua.QuaProgram.ResetFrameStatement": _reset_frame_statement,
    "google.protobuf.ListValue": _stream_processing_terminal_statement,
    # list value statement is assumed just as stream processing for now
    "qm.grpc.qua.QuaProgram.UpdateCorrectionStatement": lambda n: f'update_correction("{n.qe.name}"'
    f",{ExpressionSerializingVisitor.serialize(n.correction.c0)}"
    f",{ExpressionSerializingVisitor.serialize(n.correction.c1)}"
    f",{ExpressionSerializingVisitor.serialize(n.correction.c2)}"
    f",{ExpressionSerializingVisitor.serialize(n.correction.c3)})",
    "qm.grpc.qua.QuaProgram.SetDcOffsetStatement": _set_dc_offset_statement,
    "qm.grpc.qua.QuaProgram.AdvanceInputStreamStatement": _advance_input_stream_statement,
}

_var_type_dec = {0: "int", 1: "bool", 2: "fixed"}

_nodes_to_ignore = [
    "qm.grpc.qua.QuaProgram.Script",
    "qm.grpc.qua.QuaProgram.StatementsCollection",
    "qm.grpc.qua.QuaProgram.AnyStatement",
    "qm.grpc.qua.QuaProgram.AnyScalarExpression",
    "qm.grpc.qua.QuaProgram.BinaryExpression",
    "qm.grpc.qua.QuaProgram.VarRefExpression",
    "qm.grpc.qua.QuaProgram.LiteralExpression",
    "qm.grpc.qua.QuaProgram.PlayStatement",
    "qm.grpc.qua_config.QuaConfig",
]

_dont_print = set(list(_blocks.keys()) + list(_statements.keys()) + _nodes_to_ignore)
