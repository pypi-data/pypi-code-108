from functools import partial
from typing import Callable, Dict, List, Tuple

from centaur._.pyvmps.error_handling.constants import ExceptionMsgs as em
from centaur._.pyvmps.models.exceptions import InvalidInputException
from centaur._.pyvmps.models.tf.constants import INPUTS, INSTANCES
from centaur._.pyvmps.models.tf.utils import _extract


def batch_deconstruct(
    payload: Dict, row_format_funcs: List[Callable], col_format_funcs: List[Callable]
) -> Tuple[partial, Callable]:
    row_format_preprocess_data, row_format_create_input_tensors, row_format_handle_result = row_format_funcs
    col_format_preprocess_data, col_format_create_input_tensors, col_format_handle_result = col_format_funcs
    if payload.get(INSTANCES):
        return (
            partial(
                _extract,
                preprocess_func=row_format_preprocess_data,
                extract_data_prep_func=row_format_create_input_tensors,
                payload=payload.get(INSTANCES),
            ),
            row_format_handle_result,
        )
    elif payload.get(INPUTS):
        return (
            partial(
                _extract,
                preprocess_func=col_format_preprocess_data,
                extract_data_prep_func=col_format_create_input_tensors,
                payload=payload.get(INPUTS),
            ),
            col_format_handle_result,
        )
    raise InvalidInputException(em.TF_INVALID_INPUT_NO_KEY_FOUND)
