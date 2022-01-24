# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataTransformer feature concatenator virtual op converter."""

import sys
import numpy as np

from azureml.automl.core.onnx_convert.onnx_convert_constants import OnnxConvertConstants

# Import the onnx related packages, only if the python version is compatible.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    from skl2onnx import update_registered_converter
    from skl2onnx.proto import onnx_proto
    from skl2onnx.common.data_types import FloatType
    from skl2onnx.common.data_types import Int64Type
    from skl2onnx.common.data_types import Int64TensorType
    from skl2onnx.common.data_types import FloatTensorType

    from skl2onnx.common.utils import check_input_and_output_types
    from skl2onnx.common._apply_operation import apply_cast, apply_identity, apply_reshape, apply_mul
    from skl2onnx.operator_converters.common import convert_integer_to_float

# AutoML modules.
from ._abstract_operator_converter import _AbstractOperatorConverter  # noqa: E402


# The Virtual operator of post process the TfIdfVectorizer used by convert the DataTransformer.
class _VirtualMissingValReplaceProcessor:
    def __init__(self, *args, **kwargs):
        pass


class MissingValReplaceProcessorConverter(_AbstractOperatorConverter):
    """The TfIdfVectorizer post process virtual op converter."""

    def __init__(self):
        """Construct the TfIdfVectorizer post process virtual op converter."""
        type(self).OPERATOR_ALIAS = 'MissingValReplaceProcessorConverter'

    def setup(self):
        """Set up the converter."""
        update_registered_converter(_VirtualMissingValReplaceProcessor,
                                    MissingValReplaceProcessorConverter.OPERATOR_ALIAS,
                                    MissingValReplaceProcessorConverter._calculate_output_shapes,
                                    MissingValReplaceProcessorConverter._convert_missing_val_replace_processor)

    @staticmethod
    def _calculate_output_shapes(operator):
        check_input_and_output_types(operator, good_input_types=[FloatTensorType, Int64TensorType])
        # The output var shape is equal to the input var shape.
        N = operator.inputs[0].type.shape[0]
        C = operator.inputs[0].type.shape[1]
        operator.outputs[0].type.shape = [N, C]

    @staticmethod
    def _convert_missing_val_replace_processor(scope, operator, container):
        input_var = operator.inputs[0]
        if isinstance(input_var.type, (Int64TensorType, Int64Type)):
            input_val_name = convert_integer_to_float(scope, input_var, container)
        else:
            input_val_name = input_var.full_name

        # This part replaces all null values by nan.
        cst_nan_name = scope.get_unique_variable_name('nan_name')
        container.add_initializer(cst_nan_name, onnx_proto.TensorProto.FLOAT, [1], [np.nan])
        cst_zero_name = scope.get_unique_variable_name('zero_name')
        container.add_initializer(cst_zero_name, onnx_proto.TensorProto.FLOAT, [1], [0])

        mask_var_name = scope.get_unique_variable_name('mask_name')
        op_type = OnnxConvertConstants.Equal
        container.add_node(op_type, [input_val_name, cst_zero_name],
                           mask_var_name, op_version=11,
                           name=scope.get_unique_operator_name(op_type))

        where_out_var_name = scope.get_unique_variable_name('where_name')
        op_type = OnnxConvertConstants.Where
        container.add_node(op_type, [mask_var_name, cst_nan_name, input_val_name],
                           where_out_var_name, op_version=11,
                           name=scope.get_unique_operator_name(op_type))

        apply_identity(scope, where_out_var_name, operator.output_full_names, container)
