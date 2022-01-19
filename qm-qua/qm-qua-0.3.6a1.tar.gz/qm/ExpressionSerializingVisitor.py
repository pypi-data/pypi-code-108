from qm.QuaNodeVisitor import QuaNodeVisitor


class ExpressionSerializingVisitor(QuaNodeVisitor):
    def __init__(self) -> None:
        self._out = ""
        super().__init__()

    def _default_visit(self, node):
        print("missing expression: " + node.DESCRIPTOR.full_name)
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_VarRefExpression(self, node):
        self._out = node.name if node.name else f"IO{node.ioNumber}"

    def visit_qm_grpc_qua_QuaProgram_ArrayVarRefExpression(self, node):
        self._out = node.name

    def visit_qm_grpc_qua_QuaProgram_ArrayCellRefExpression(self, node):
        var = ExpressionSerializingVisitor.serialize(node.arrayVar)
        index = ExpressionSerializingVisitor.serialize(node.index)
        self._out = f"{var}[{index}]"

    def visit_qm_grpc_qua_QuaProgram_LiteralExpression(self, node):
        self._out = node.value

    def visit_qm_grpc_qua_QuaProgram_AssignmentStatement_Target(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_MeasureProcess(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_AnalogMeasureProcess(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_AnalogMeasureProcess_DemodIntegration(self, node):
        name = node.integration.name
        output = node.elementOutput
        target_desc, target_value = node.target.ListFields()[0]
        if target_desc.name == "scalarProcess":
            target = ExpressionSerializingVisitor.serialize(target_value)
            self._out = f'demod.full("{name}", {target}, "{output}")'
        elif target_desc.name == "vectorProcess":
            target = ExpressionSerializingVisitor.serialize(target_value.array)

            time_desc, time_value = target_value.timeDivision.ListFields()[0]
            if time_desc.name == "sliced":
                self._out = f'demod.sliced("{name}", {target}, {time_value.samplesPerChunk}, "{output}")'
            elif time_desc.name == "accumulated":
                self._out = f'demod.accumulated("{name}", {target}, {time_value.samplesPerChunk}, "{output}")'
            elif time_desc.name == "movingWindow":
                self._out = f'demod.moving_window("{name}", {target}, {time_value.samplesPerChunk}, {time_value.chunksPerWindow}, "{output}")'
            else:
                raise Exception("Unsupported analog process target " + target_desc.name)
        else:
            raise Exception("Unsupported analog process target " + target_desc.name)

    def visit_qm_grpc_qua_QuaProgram_AnalogMeasureProcess_BareIntegration(self, node):
        name = node.integration.name
        output = node.elementOutput
        target_desc, target_value = node.target.ListFields()[0]
        if target_desc.name == "scalarProcess":
            target = ExpressionSerializingVisitor.serialize(target_value)
            self._out = f'integration.full("{name}", {target}, "{output}")'
        elif target_desc.name == "vectorProcess":
            target = ExpressionSerializingVisitor.serialize(target_value.array)

            time_desc, time_value = target_value.timeDivision.ListFields()[0]
            if time_desc.name == "sliced":
                self._out = f'integration.sliced("{name}", {target}, {time_value.samplesPerChunk}, "{output}")'
            elif time_desc.name == "accumulated":
                self._out = f'integration.accumulated("{name}", {target}, {time_value.samplesPerChunk}, "{output}")'
            elif time_desc.name == "movingWindow":
                self._out = f'integration.moving_window("{name}", {target}, {time_value.samplesPerChunk}, {time_value.chunksPerWindow}, "{output}")'
            else:
                raise Exception("Unsupported analog process target " + target_desc.name)
        else:
            raise Exception("Unsupported analog process target " + target_desc.name)

    def visit_qm_grpc_qua_QuaProgram_AnalogMeasureProcess_DualDemodIntegration(
        self, node
    ):
        name1 = node.integration1.name
        name2 = node.integration2.name
        output1 = node.elementOutput1
        output2 = node.elementOutput2
        target_desc, target_value = node.target.ListFields()[0]
        if target_desc.name == "scalarProcess":
            target = ExpressionSerializingVisitor.serialize(target_value)
            self._out = f'dual_demod.full("{name1}", "{output1}", "{name2}", "{output2}", {target})'
        elif target_desc.name == "vectorProcess":
            target = ExpressionSerializingVisitor.serialize(target_value.array)

            time_desc, time_value = target_value.timeDivision.ListFields()[0]
            if time_desc.name == "sliced":
                self._out = f'dual_demod.sliced("{name1}", "{output1}", "{name2}", "{output2}", {time_value.samplesPerChunk}, {target})'
            elif time_desc.name == "accumulated":
                self._out = f'dual_demod.accumulated("{name1}", "{output1}", "{name2}", "{output2}", {time_value.samplesPerChunk}, {target})'
            elif time_desc.name == "movingWindow":
                self._out = f'dual_demod.moving_window("{name1}", "{output1}", "{name2}", "{output2}", {time_value.samplesPerChunk}, {time_value.chunksPerWindow}, {target})'
            else:
                raise Exception("Unsupported analog process target " + target_desc.name)
        else:
            raise Exception("Unsupported analog process target " + target_desc.name)

    def visit_qm_grpc_qua_QuaProgram_AnalogMeasureProcess_DualBareIntegration(
        self, node
    ):
        name1 = node.integration1.name
        name2 = node.integration2.name
        output1 = node.elementOutput1
        output2 = node.elementOutput2
        target_desc, target_value = node.target.ListFields()[0]
        if target_desc.name == "scalarProcess":
            target = ExpressionSerializingVisitor.serialize(target_value)
            self._out = f'dual_integration.full("{name1}", "{output1}", "{name2}", "{output2}", {target})'
        elif target_desc.name == "vectorProcess":
            target = ExpressionSerializingVisitor.serialize(target_value.array)

            time_desc, time_value = target_value.timeDivision.ListFields()[0]
            if time_desc.name == "sliced":
                self._out = f'dual_integration.sliced("{name1}", "{output1}", "{name2}", "{output2}", {time_value.samplesPerChunk}, {target})'
            elif time_desc.name == "accumulated":
                self._out = f'dual_integration.accumulated("{name1}", "{output1}", "{name2}", "{output2}", {time_value.samplesPerChunk}, {target})'
            elif time_desc.name == "movingWindow":
                self._out = f'dual_integration.moving_window("{name1}", "{output1}", "{name2}", "{output2}", {time_value.samplesPerChunk}, {time_value.chunksPerWindow}, {target})'
            else:
                raise Exception("Unsupported analog process target " + target_desc.name)
        else:
            raise Exception("Unsupported analog process target " + target_desc.name)

    def visit_qm_grpc_qua_QuaProgram_AnalogMeasureProcess_RawTimeTagging(self, node):
        target = ExpressionSerializingVisitor.serialize(node.target)
        target_len = ExpressionSerializingVisitor.serialize(node.targetLen)
        max_time = node.maxTime
        element_output = node.elementOutput
        self._out = f'time_tagging.analog({target}, {max_time}, {target_len}, "{element_output}")'

    def visit_qm_grpc_qua_QuaProgram_DigitalMeasureProcess(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_DigitalMeasureProcess_Counting(self, node):
        element_outputs = []
        for element_output in node.elementOutputs:
            element_outputs.append(f'"{element_output}"')
        element_outputs_str = ",".join(element_outputs)
        target = ExpressionSerializingVisitor.serialize(node.target)
        max_time = node.maxTime
        self._out = f"counting.digital({target}, {max_time}, ({element_outputs_str}))"

    def visit_qm_grpc_qua_QuaProgram_AnalogProcessTarget_ScalarProcessTarget(
        self, node
    ):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_AnalogProcessTarget_TimeDivision(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_AnyScalarExpression(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_SaveStatement_Source(self, node):
        super()._default_visit(node)

    def visit_qm_grpc_qua_QuaProgram_BinaryExpression(self, node):
        left = ExpressionSerializingVisitor.serialize(node.left)
        right = ExpressionSerializingVisitor.serialize(node.right)
        sop = node.op
        if sop == node.ADD:
            op = "+"
        elif sop == node.SUB:
            op = "-"
        elif sop == node.GT:
            op = ">"
        elif sop == node.LT:
            op = "<"
        elif sop == node.LET:
            op = "<="
        elif sop == node.GET:
            op = ">="
        elif sop == node.EQ:
            op = "=="
        elif sop == node.MULT:
            op = "*"
        elif sop == node.DIV:
            op = "/"
        elif sop == node.OR:
            op = "|"
        elif sop == node.AND:
            op = "&"
        elif sop == node.XOR:
            op = "^"
        elif sop == node.SHL:
            op = "<<"
        elif sop == node.SHR:
            op = ">>"
        else:
            raise Exception("Unsupported operator " + sop)
        self._out = f"{left}{op}{right}"

    @staticmethod
    def serialize(node) -> str:
        visitor = ExpressionSerializingVisitor()
        visitor.visit(node)
        return visitor._out
