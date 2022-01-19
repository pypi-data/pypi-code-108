"""
Helper functions to handle TF1 formatting and extracting of tensors
"""
from collections import defaultdict
from typing import Dict, List, Collection

import tensorflow as tf

from centaur._.pyvmps.error_handling.constants import ExceptionMsgs as em
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.exceptions import InvalidInputException
from centaur._.pyvmps.models.tf.constants import (
    COL_FORMAT_NESTED_LIST,
    COL_FORMAT_OBJECT,
    COL_FORMAT_VALUE,
    OUTPUTS,
    PREDICTIONS,
    ROW_FORMAT_LIST_OF_OBJECTS,
    ROW_FORMAT_NESTED_LIST,
    ROW_FORMAT_VALUE,
    INPUT_KEY_TO_TENSOR,
)
from centaur._.pyvmps.models.tf.utils import (
    _determine_col_format_type,
    _determine_row_format_type,
    output_to_col_format_json,
    output_to_row_format_json,
)
from centaur._.pyvmps.models.tf.types import ExtractDataFunc, InputTensorsMap, InferenceRes

_logger = get_logger(__name__)


def row_format_create_input_tensors(payload: List) -> ExtractDataFunc:
    """row_format_create_input_tensors.

    :param payload: request payload, ie the body of the http request {"signature_name": "", "instances": ".."}
    :type payload: List
    :rtype: Callable
    """
    # payload here is the data pass to the tf model
    payload_type = _determine_row_format_type(payload)

    def _extract_data(indiv_sig_data: Dict) -> InputTensorsMap:
        """Converts the http request body from json format to a Dict with Input Tensor objects as Keys
        and input data as values. Output can be passed in as feed dict for TF1

        :param indiv_sig_data: Dict containing TENSOR_TO_INPUT_KEY and OUTPUT_KEY_TO_TENSOR keys.
        :type indiv_sig_data: Dict
        :rtype: Dict[tf.Tensor, List]
        """
        _logger.debug("_row_extract_data_start")
        input_tensors_tpl = indiv_sig_data[INPUT_KEY_TO_TENSOR]
        single_input_tensor = len(input_tensors_tpl) == 1

        input_tensors: Dict = defaultdict(list)
        if payload_type == ROW_FORMAT_VALUE or payload_type == ROW_FORMAT_NESTED_LIST:
            # Row format, value or nested list
            if not single_input_tensor:
                raise InvalidInputException(em.TF_INVALID_INPUT_KEY_NOT_SPECIFIED)
            tensor = list(input_tensors_tpl.values())[0]
            # NOTE: Wrap payload in list if its a single value so http_request level batching
            # can append subsequent tensor inputs without any errors
            input_tensors[tensor] = [payload] if payload_type == ROW_FORMAT_VALUE else payload
        elif payload_type == ROW_FORMAT_LIST_OF_OBJECTS:
            # Row format, list of objects
            for input_key, tensor in input_tensors_tpl.items():
                for obj in payload:
                    if not obj.get(input_key):
                        raise InvalidInputException(em.TF_INVALID_INPUT_MISSING_KEY.format(input_key=input_key))
                    input_tensors[tensor].append(obj[input_key])
        _logger.debug("_row_extract_data_end")
        return input_tensors

    return _extract_data


def row_format_handle_result(model_output: Dict) -> InferenceRes:
    """Convert model_output into format expected when a row-formatted payload was sent

    :param model_output: Result produced by model
    """
    _logger.debug("_row_format_handle_result")
    result = output_to_row_format_json(model_output)
    return {PREDICTIONS: result}


def col_format_create_input_tensors(payload: Dict) -> ExtractDataFunc:
    """col_format_create_input_tensors.

    :param payload:
    """
    payload_type = _determine_col_format_type(payload)

    def _extract_data(indiv_sig_data: Dict) -> InputTensorsMap:
        _logger.debug("_col_extract_data_start")
        input_tensors_tpl = indiv_sig_data[INPUT_KEY_TO_TENSOR]
        single_input_tensor = len(input_tensors_tpl) == 1
        input_tensors: Dict[tf.Tensor, Collection] = {}
        if payload_type == COL_FORMAT_VALUE or payload_type == COL_FORMAT_NESTED_LIST:
            if not single_input_tensor:
                raise InvalidInputException(em.TF_INVALID_INPUT_KEY_NOT_SPECIFIED)
            tensor = list(input_tensors_tpl.values())[0]
            # NOTE: Wrap payload in list if its a single value so http_request level batching
            # can append subsequent tensor inputs without any errors
            input_tensors[tensor] = [payload] if payload_type == COL_FORMAT_VALUE else payload
        elif payload_type == COL_FORMAT_OBJECT:
            for input_key, tensor in input_tensors_tpl.items():
                if input_key not in payload:
                    raise InvalidInputException(em.TF_INVALID_INPUT_MISSING_KEY.format(input_key=input_key))
                input_tensors[tensor] = payload[input_key]
        _logger.debug("_col_extract_data_end")
        return input_tensors

    return _extract_data


def col_format_handle_result(res: Dict) -> InferenceRes:
    _logger.debug("_col_format_handle_result")
    result = output_to_col_format_json(res)
    return {OUTPUTS: result}
