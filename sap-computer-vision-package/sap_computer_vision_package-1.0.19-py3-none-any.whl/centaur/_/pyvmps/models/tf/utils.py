import base64
import io
from typing import Dict, List, Union, Tuple

from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.tf.constants import (
    B64_KEY,
    COL_FORMAT_NESTED_LIST,
    COL_FORMAT_OBJECT,
    COL_FORMAT_VALUE,
    ROW_FORMAT_LIST_OF_OBJECTS,
    ROW_FORMAT_NESTED_LIST,
    ROW_FORMAT_VALUE,
)
from centaur._.pyvmps.models.tf.types import (
    RowExtractDataPrepFunc,
    ColExtractDataPrepFunc,
    Tf2RowExtractDataPrepFunc,
    Tf2ColExtractDataPrepFunc,
    RowPreprocessFunc,
    ColPreprocessFunc,
    HandleResFunc,
    InferenceFunc,
    InferenceRes,
    RawPayload,
    IndivSigData,
)

logger = get_logger(__file__)


def convert_value_to_list(output: Dict) -> Dict:
    return {k: v.tolist() for k, v in output.items()}


def output_to_row_format_json(output_to_format: Dict) -> Union[Dict, List]:
    # only affects http rest calls
    output = output_to_format.copy()
    processed_output = convert_value_to_list(output)
    num_outputs = len(list(output.keys()))
    num_inputs = len(list(output.values())[0])
    if num_outputs == 1:
        result = list(processed_output.values())[0]
    else:
        response: List[Dict] = []
        for i in range(num_inputs):
            temp_dict: Dict = {}
            for k, v in processed_output.items():
                temp_dict[k] = v[i]
            response.append(temp_dict)
        result = response
    return result


def output_to_col_format_json(output: Dict) -> Dict:
    # TODO: Temp fix. Perform single key conversion in HTTPServerUDSMessage
    processed_output = convert_value_to_list(output)
    return processed_output


def handle_col_format_single_key(output: Dict):
    num_outputs = len(list(output.keys()))
    if num_outputs == 1:
        return list(output.values())[0]
    return output


def handle_row_format_single_key(output: Dict):
    num_outputs = len(list(output.keys()))
    if num_outputs == 1:
        return list(output.values())[0]
    return output


Base64Str = str


def is_base64(value: str) -> bool:
    try:
        return base64.b64encode(base64.b64decode(value)).decode("utf-8") == value
    except Exception:
        logger.exception("error")
        return False


def convert_b64_to_byte_array(value: Base64Str) -> bytes:
    return io.BytesIO(base64.b64decode(value)).getvalue()


def handle_b64_case(value: str):
    if isinstance(value, str) and is_base64(value):
        return convert_b64_to_byte_array(value)
    return value


# >>>>>>>>> Row Format Functions <<<<<<<<<<<
def _determine_row_format_type(payload: List) -> str:
    """Get the sub-type of the row-formatted payload.
    Assumes row object type can only be list or value, determine by checking first element in list.
    Not the best the solution,

    :param payload:
    :type payload: List
    :rtype: str

    """
    if isinstance(payload, list) and len(payload) > 0:
        if isinstance(payload[0], list):
            return ROW_FORMAT_NESTED_LIST
        elif isinstance(payload[0], dict):
            return ROW_FORMAT_LIST_OF_OBJECTS
    return ROW_FORMAT_VALUE


def row_format_preprocess_data(input_payload: List) -> List:
    """Handle preprocessing of http request body for row-formatted payloads.
    Should be called before row_format_create_input_tensors

    :param input_payload:
    :type input_payload: List
    :rtype: List
    """
    payload = input_payload
    for i in range(len(payload)):
        # introduce mutation, check with leo
        obj = payload[i]
        if isinstance(obj, dict) and len(obj) == 1 and obj.get(B64_KEY):
            payload[i] = convert_b64_to_byte_array(obj[B64_KEY])
        else:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict) and value.get(B64_KEY):
                        obj[key] = convert_b64_to_byte_array(value[B64_KEY])
    return payload


# >>>> Col format functions <<<<
def _determine_col_format_type(payload: Dict) -> str:
    # assumes row object type can only be list or value, determine by checking first element in list.
    # Not the best the solution, will do for now
    # payload here is a LIST
    if isinstance(payload, list):
        return COL_FORMAT_NESTED_LIST
    elif isinstance(payload, dict):
        return COL_FORMAT_OBJECT
    return COL_FORMAT_VALUE


def col_format_preprocess_data(input_payload: Dict) -> Dict:
    """col_format_preprocess_data.

    :param input_payload:
    :type input_payload: Dict
    :rtype: Dict
    """
    payload = input_payload
    if isinstance(payload, list):
        for i in range(len(payload)):
            obj = payload[i]
            if isinstance(obj, dict) and len(obj) == 1 and obj.get(B64_KEY):
                payload[i] = convert_b64_to_byte_array(obj[B64_KEY])
    elif isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, list):
                for index in range(len(value)):
                    item = value[index]
                    if isinstance(item, dict) and item.get(B64_KEY):
                        value[index] = convert_b64_to_byte_array(item[B64_KEY])
    return payload


def _execute(
    *,
    preprocess_func: Tuple[RowPreprocessFunc, ColPreprocessFunc],
    extract_data_prep_func: Tuple[RowExtractDataPrepFunc, ColExtractDataPrepFunc],
    output_format_func: HandleResFunc,
    inference_func: InferenceFunc,
    payload: RawPayload,
    indiv_sig_data: IndivSigData
) -> InferenceRes:
    # reuse for tf2
    processed_input = preprocess_func(payload)
    predict_input = extract_data_prep_func(processed_input)(indiv_sig_data)
    res = inference_func(predict_input)
    return output_format_func(res)


def _extract(
    *,
    preprocess_func: Tuple[RowPreprocessFunc, ColPreprocessFunc],
    extract_data_prep_func: Tuple[
        RowExtractDataPrepFunc, ColExtractDataPrepFunc, Tf2RowExtractDataPrepFunc, Tf2ColExtractDataPrepFunc
    ],
    payload: RawPayload,
    indiv_sig_data: IndivSigData
) -> Dict:
    """_extract is used by BatchPredict functions

    :param preprocess_func:
    :param extract_data_prep_func:
    :param payload:
    :param indiv_sig_data:
    :rtype: Dict
    """
    processed_input = preprocess_func(payload)
    return extract_data_prep_func(processed_input)(indiv_sig_data)
