from functools import partial
from typing import Dict, List, Callable

import tensorflow as tf

from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.base_model import Model
from centaur._.pyvmps.models.exceptions import InvalidSignatureKeyException
from centaur._.pyvmps.models.tf import constants as tfconstants
from centaur._.pyvmps.models.tf.constants import SigTensorInfo
from centaur._.pyvmps.models.tf.tf2.payload_utils import (
    tf2_col_format_create_input_tensors,
    tf2_col_format_handle_result,
    tf2_row_format_create_input_tensors,
    tf2_row_format_handle_result,
)
from centaur._.pyvmps.models.tf.utils import (
    _execute,
    col_format_preprocess_data,
    # deconstruct,
    row_format_preprocess_data,
)
from centaur._.pyvmps.models.tf.constants import INPUTS, INSTANCES
from centaur._.pyvmps.models.tf.types import FormatLoadedFunc, RawPayload, InferenceRes
from centaur._.pyvmps.error_handling.constants import ExceptionMsgs as em
from centaur._.pyvmps.models.exceptions import InvalidInputException

_logger = get_logger(__name__)


def load_func_row_payload() -> FormatLoadedFunc:
    # for row formatted incoming payloads
    return partial(
        _execute,
        preprocess_func=row_format_preprocess_data,
        extract_data_prep_func=tf2_row_format_create_input_tensors,
        output_format_func=tf2_row_format_handle_result,
    )


def load_func_col_payload() -> FormatLoadedFunc:
    # for col formatted incoming payloads
    return partial(
        _execute,
        preprocess_func=col_format_preprocess_data,
        extract_data_prep_func=tf2_col_format_create_input_tensors,
        output_format_func=tf2_col_format_handle_result,
    )


def predict(payload, sig_tensor_dict: Dict[str, SigTensorInfo]) -> InferenceRes:
    def _predict(input_tensors) -> Dict:
        return conc_func(**input_tensors)

    signature = payload.get(tfconstants.SIGNATURE_NAME, tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY)
    sig_tensor = sig_tensor_dict.get(signature, None)
    if not sig_tensor:
        raise InvalidSignatureKeyException("Invalid signature '{}'".format(signature))
    conc_func: Callable = sig_tensor.conc_func
    if payload.get(INSTANCES):
        inference_payload: RawPayload = payload.get(INSTANCES)
        format_loaded_func: FormatLoadedFunc = load_func_row_payload()
    elif payload.get(INPUTS):
        inference_payload = payload.get(INPUTS)
        format_loaded_func = load_func_col_payload()
    else:
        raise InvalidInputException(em.TF_INVALID_INPUT_NO_KEY_FOUND)
    try:
        res: InferenceRes = format_loaded_func(
            payload=inference_payload, indiv_sig_data=sig_tensor, inference_func=_predict
        )
        return res
    except Exception as e:
        _logger.exception("Error occured calling model predict method")
        # raise ModelPredictErrorException from e
        raise e


class Tf2Model(Model):
    """Tf2Model."""

    @staticmethod
    def get_verbs() -> List[str]:
        return [tfconstants.TfVerbs.PREDICT]

    def __init__(self, dir_of_saved_model: str):
        self.dir_of_saved_model = dir_of_saved_model

    def load(self) -> bool:
        gpus = tf.config.experimental.list_physical_devices("GPU")
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices("GPU")
                _logger.info("logical_gpus=%s,physical_gpus=%s", len(logical_gpus), len(gpus))
            except RuntimeError:
                _logger.exception("gpu_set_memory_growth")
        try:
            model = tf.saved_model.load(self.dir_of_saved_model)  # pylint:disable=no-value-for-parameter
        except ValueError:
            model = tf.keras.models.load_model(self.dir_of_saved_model)  # pylint:disable=no-value-for-parameter

        signatures = model.signatures
        sig_tensor_dict = {}
        for sig_name, conc_func in signatures.items():
            sig_tensor_dict[sig_name] = SigTensorInfo(
                inputs=conc_func.structured_input_signature[1],
                outputs=conc_func.structured_outputs,
                conc_func=conc_func,
                model=model,  # store reference to model here as it is used by the signature under the hood (even though it's not used explicitly)
            )
        self.set_tf2_model_attrs(sig_tensor_dict)
        return super().load()

    def set_tf2_model_attrs(self, sig_tensor_dict: Dict[str, SigTensorInfo]):
        self.sig_tensor_dict = sig_tensor_dict
        self.verb_funcs = {tfconstants.TfVerbs.PREDICT: self.predict}

    def predict(self, payload):
        return predict(payload, self.sig_tensor_dict)
