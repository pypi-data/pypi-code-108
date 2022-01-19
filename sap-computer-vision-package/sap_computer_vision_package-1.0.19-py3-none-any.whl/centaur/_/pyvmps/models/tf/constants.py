# for now use constants from here, unless theres another source that has these same values
from collections import namedtuple

from centaur import constants

INPUTS = constants.TF.inputs
INSTANCES = "instances"

ROW_FORMAT_NESTED_LIST = "ROW_FORMAT_NESTED_LIST"
ROW_FORMAT_LIST_OF_OBJECTS = "ROW_FORMAT_LIST_OF_OBJECTS"
ROW_FORMAT_VALUE = "ROW_FORMAT_VALUE"
B64_KEY = "b64"


COL_FORMAT_NESTED_LIST = "COL_FORMAT_NESTED_LIST"
COL_FORMAT_VALUE = "COL_FORMAT_VALUE"
COL_FORMAT_OBJECT = "COL_FORMAT_OBJECT"

PREDICTIONS = "predictions"
OUTPUTS = "outputs"

SIGNATURE_NAME = constants.TF.signature_name

OUTPUT_KEY_TO_TENSOR = "output_key_to_tensor"
INPUT_KEY_TO_TENSOR = "input_key_to_tensor"

FETCHES = "fetches"
MERGED_INPUT_TENSORS = "merged_input_tensors"
OUTPUT_FORMATTER_REQ_ID_MAPPER = "output_formatter_req_id_mapper"
CONC_FUNC = "conc_func"


TfMergedRequestsTuple = namedtuple("TfMergedRequestsTuple", ["req_id", "start_index", "end_index", "formatter"])
SigTensorInfo = namedtuple("SigTensorInfo", ["inputs", "outputs", "conc_func", "model"])


class TfVerbs:
    """TfVerbs."""

    PREDICT = "predict"
