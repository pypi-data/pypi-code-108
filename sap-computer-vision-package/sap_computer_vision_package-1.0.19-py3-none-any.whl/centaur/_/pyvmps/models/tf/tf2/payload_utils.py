# pylint: disable=no-member
from typing import Dict, List

import tensorflow as tf

from centaur._.pyvmps.error_handling.constants import ExceptionMsgs as em
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.exceptions import InvalidInputException, InvalidInputTensorShape
from centaur._.pyvmps.models.tf.constants import (
    COL_FORMAT_NESTED_LIST,
    COL_FORMAT_OBJECT,
    COL_FORMAT_VALUE,
    ROW_FORMAT_LIST_OF_OBJECTS,
    ROW_FORMAT_NESTED_LIST,
    ROW_FORMAT_VALUE,
    SigTensorInfo,
)
from centaur._.pyvmps.models.tf.tf1.payload_utils import (
    _determine_col_format_type,
    _determine_row_format_type,
    col_format_handle_result,
    row_format_handle_result,
)
from centaur._.pyvmps.models.tf.types import InferenceRes, Tf2ExtractDataFunc


_logger = get_logger(__name__)


def tf2_row_format_create_input_tensors(payload: List) -> Tf2ExtractDataFunc:
    """row_format_create_input_tensors.

    :param payload: request payload, ie the body of the http request {"signature_name": "", "instances": ".."}
    :type payload: List
    :rtype: Callable
    """
    # payload here is the data pass to the tf model
    payload_type = _determine_row_format_type(payload)

    def _extract_data(sig_tensor_info: SigTensorInfo) -> Dict:
        """_extract_data.

        :param sig_tensor_info:
        :type sig_tensor_info: SigTensorInfo
        :rtype: Dict[str, tf.EagerTensor]
        """
        input_data_dict: Dict[str, tf.constant] = {}
        structured_input_sig: Dict = sig_tensor_info.inputs
        single_input_tensor = len(structured_input_sig)
        if payload_type == ROW_FORMAT_VALUE or payload_type == ROW_FORMAT_NESTED_LIST:
            # Row format, value or nested list
            if not single_input_tensor:
                raise InvalidInputException(
                    # "Input keys not specified in data"
                    em.TF_INVALID_INPUT_KEY_NOT_SPECIFIED
                )
            key_name = list(structured_input_sig.keys())[0]
            payload_dtype = structured_input_sig[key_name].dtype
            input_required_tensor_shape: tf.TensorShape = structured_input_sig[key_name].shape
            newly_created_tensor = tf.constant(payload[key_name], dtype=payload_dtype)
            if not input_required_tensor_shape.is_compatible_with(newly_created_tensor.shape):
                raise InvalidInputTensorShape(
                    # "Expected={}, gave={}".format(
                    #     input_required_tensor_shape, newly_created_tensor.shape
                    # )
                    em.TF_INVALID_INPUT_TENSOR_SHAPE.format(
                        expected_shape=input_required_tensor_shape, received_shape=newly_created_tensor.shape
                    )
                )
            input_data_dict[key_name] = tf.constant(payload[key_name], dtype=payload_dtype)
        elif payload_type == ROW_FORMAT_LIST_OF_OBJECTS:

            for input_name, input_tensor in structured_input_sig.items():
                input_data: List = []

                for obj in payload:
                    if not obj.get(input_name):
                        raise InvalidInputException(
                            em.TF_INVALID_INPUT_MISSING_KEY.format(input_key=input_name)
                            # "Data does not contain {} input key".format(input_name)
                        )
                    input_data.append(obj[input_name])
                tensor_shape: tf.TensorShape = input_tensor.shape
                newly_created_tensor = tf.constant(input_data, dtype=input_tensor.dtype)
                if not tensor_shape.is_compatible_with(newly_created_tensor.shape):
                    raise InvalidInputTensorShape(
                        # "Expected={}, gave={}".format(
                        #     tensor_shape, newly_created_tensor.shape
                        # )
                        em.TF_INVALID_INPUT_TENSOR_SHAPE.format(
                            expected_shape=tensor_shape, received_shape=newly_created_tensor.shape
                        )
                    )
                input_data_dict[input_name] = newly_created_tensor
        return input_data_dict

    return _extract_data


def tf2_row_format_handle_result(model_output: Dict) -> InferenceRes:
    """Convert model_output into format expected when a row-formatted payload was sent

    :param model_output: Result produced by model
    """
    _logger.debug("_row_format_handle_result")
    # convert EagerTensor to numpy array first before passing to format_result()
    model_output = {k: v.numpy() for k, v in model_output.items()}
    return row_format_handle_result(model_output)


def tf2_col_format_create_input_tensors(payload: Dict) -> Tf2ExtractDataFunc:
    """col_format_create_input_tensors.

    :param payload:
    """
    payload_type = _determine_col_format_type(payload)

    def _extract_data(sig_tensor_info: SigTensorInfo) -> Dict:
        """_extract_data.

        :param sig_tensor_info:
        :rtype: Dict[str, tf.EagerTensor]
        """
        input_data_dict: Dict[str, tf.constant] = {}
        structured_input_sig: Dict[str, tf.TensorSpec] = sig_tensor_info.inputs
        single_input_tensor = len(structured_input_sig) == 1
        if payload_type == COL_FORMAT_VALUE or payload_type == COL_FORMAT_NESTED_LIST:
            if not single_input_tensor:
                raise InvalidInputException(em.TF_INVALID_INPUT_KEY_NOT_SPECIFIED)
            key_name = list(structured_input_sig.keys())[0]
            payload_dtype = structured_input_sig[key_name].dtype
            input_required_tensor_shape: tf.TensorShape = structured_input_sig[key_name].shape
            newly_created_tensor = tf.constant(payload[key_name], dtype=payload_dtype)
            if not input_required_tensor_shape.is_compatible_with(newly_created_tensor.shape):
                raise InvalidInputTensorShape(
                    # "Expected={}, gave={}".format(
                    #     input_required_tensor_shape, newly_created_tensor.shape
                    # )
                    em.TF_INVALID_INPUT_TENSOR_SHAPE.format(
                        expected_shape=input_required_tensor_shape, received_shape=newly_created_tensor.shape
                    )
                )
            input_data_dict[key_name] = tf.constant(payload[key_name], dtype=payload_dtype)
        elif payload_type == COL_FORMAT_OBJECT:
            for input_key, input_tensor in structured_input_sig.items():
                if input_key not in payload:
                    raise InvalidInputException(
                        # "Data does not contain {} input key".format(input_key)
                        em.TF_INVALID_INPUT_MISSING_KEY.format(input_key=input_key)
                    )
                tensor_shape: tf.TensorShape = input_tensor.shape
                newly_created_tensor = tf.constant(payload[input_key], dtype=input_tensor.dtype)
                if not tensor_shape.is_compatible_with(newly_created_tensor.shape):
                    raise InvalidInputTensorShape(
                        # "Expected={}, gave={}".format(
                        #     tensor_shape, newly_created_tensor.shape
                        # )
                        em.TF_INVALID_INPUT_TENSOR_SHAPE.format(
                            expected_shape=tensor_shape, received_shape=newly_created_tensor.shape
                        )
                    )
                input_data_dict[input_key] = newly_created_tensor
        return input_data_dict

    return _extract_data


def tf2_col_format_handle_result(res) -> InferenceRes:
    """tf2_col_format_handle_result.

    :param res:
    """
    _logger.debug("_col_format_handle_result")
    res = {k: v.numpy() for k, v in res.items()}
    return col_format_handle_result(res)
