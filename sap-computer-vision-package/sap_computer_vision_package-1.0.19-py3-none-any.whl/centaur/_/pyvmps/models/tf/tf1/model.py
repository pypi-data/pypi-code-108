from functools import partial
from typing import Dict, List, Optional, Callable

import tensorflow as tf  # type: ignore
from tensorflow.python.client import device_lib

from centaur._.pyvmps.error_handling.constants import ExceptionMsgs as em
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.base_model import Model


from centaur._.pyvmps.models.exceptions import InvalidSignatureKeyException
from centaur._.pyvmps.models.tf import constants as tfconstants
from centaur._.pyvmps.models.tf.tf1.payload_utils import (
    col_format_create_input_tensors,
    col_format_handle_result,
    row_format_create_input_tensors,
    row_format_handle_result,
)
from centaur._.pyvmps.models.tf.utils import _execute, col_format_preprocess_data, row_format_preprocess_data
from centaur._.pyvmps.models.tf.constants import INPUTS, INSTANCES
from centaur._.pyvmps.models.exceptions import InvalidInputException
from centaur._.pyvmps.models.tf.types import FormatLoadedFunc, IndivSigData, InferenceRes, RawPayload

_logger = get_logger(__file__)


def load_func_row_payload() -> FormatLoadedFunc:
    """load_func_row_payload sets up _execute() with functions that
    can handle row formatted payloads. Curries and returns a partial function
    that expects [inference_func, payload, indiv_sig_data] as parameters

    :rtype: FormatLoadedFunc
    """
    # for row formatted incoming payloads
    return partial(
        _execute,
        preprocess_func=row_format_preprocess_data,
        extract_data_prep_func=row_format_create_input_tensors,
        output_format_func=row_format_handle_result,
    )


def load_func_col_payload() -> FormatLoadedFunc:
    """load_func_col_payload sets up _execute() with functions that handle col formatted payloads
    Also returns a FormatLoadedFunc

    :rtype: FormatLoadedFunc
    """
    # for col formatted incoming payloads
    return partial(
        _execute,
        preprocess_func=col_format_preprocess_data,
        extract_data_prep_func=col_format_create_input_tensors,
        output_format_func=col_format_handle_result,
    )


def _predict(sess, fetches: Dict) -> Callable[[Dict], Dict]:
    def __inner(feed_dict) -> Dict:
        return sess.run(fetches, feed_dict)

    return __inner


def predict(payload: Dict, sess, signature_tensor_mapping: Dict[str, IndivSigData]) -> InferenceRes:
    """build_inference_func_v2.

    :param sess:
    :type sess: tf.Session
    :param signature_tensor_mapping:
    :type signature_tensor_mapping: Dict[str, IndivSigData]
    :param sig:
    :type sig: str
    """

    sig: str = payload.get(tfconstants.SIGNATURE_NAME, tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY)
    tensor_mapping_dict: Optional[Dict] = signature_tensor_mapping.get(sig, None)
    if not tensor_mapping_dict:
        raise InvalidSignatureKeyException(em.TF_INVALID_SIGNATURE_KEY.format(signature=sig))
    fetches: Dict = tensor_mapping_dict[tfconstants.OUTPUT_KEY_TO_TENSOR]
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
            payload=inference_payload, indiv_sig_data=tensor_mapping_dict, inference_func=_predict(sess, fetches)
        )
        return res
    except Exception as e:
        _logger.exception("Error occured calling model predict method")
        raise e


class Tf1Model(Model):
    """Model returned when ModelLoader.load is called. This is for local testing use"""

    def __init__(self, dir_of_saved_model: str):
        self.dir_of_saved_model = dir_of_saved_model

    def set_tf1_model_attrs(self, sess, sig_mapping: Dict[str, IndivSigData]):
        self.sess = sess
        self.sig_mapping = sig_mapping
        self.verb_funcs = {tfconstants.TfVerbs.PREDICT: self.predict}

    def load(self) -> bool:
        try:
            _logger.debug("Tensorflow GPU check running without device_lib")
            gpus = tf.config.experimental.list_physical_devices("GPU")
        except AttributeError:
            _logger.debug("Tensorflow GPU check running using device_lib")

            try:
                local_device_protos = device_lib.list_local_devices()
                gpus = [x.name for x in local_device_protos if x.device_type == "GPU"]
            except Exception as ex:
                _logger.debug("Tensorflow GPU check unsuccessful on device_lib method=%s", ex)

        if gpus:
            _logger.info("tf1 physical_gpus=%s", len(gpus))

        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True  # pylint: disable=no-member
        sess = tf.compat.v1.Session(config=config)

        if hasattr(tf.compat.v1.saved_model, "load"):
            graph_meta_def = tf.compat.v1.saved_model.load(sess, [tf.saved_model.SERVING], self.dir_of_saved_model)
        else:
            graph_meta_def = tf.compat.v1.saved_model.loader.load(
                sess, [tf.saved_model.SERVING], self.dir_of_saved_model
            )
        signature = graph_meta_def.signature_def

        signature_tensor_mapping: Dict[str, IndivSigData] = {}
        for signature_name in signature.keys():
            # For each signature, create mapping for input tensor and output tensor
            indiv_sig_data = signature_tensor_mapping[signature_name] = {
                tfconstants.INPUT_KEY_TO_TENSOR: {},  # Dict[str: Tensor]
                tfconstants.OUTPUT_KEY_TO_TENSOR: {},  # Dict[str: Tensor]
            }

            inputs = signature[signature_name].inputs
            for k in inputs.keys():
                tensor = sess.graph.get_tensor_by_name(inputs[k].name)
                indiv_sig_data[tfconstants.INPUT_KEY_TO_TENSOR][k] = tensor

            outputs = signature[signature_name].outputs
            for k in outputs.keys():
                tensor = sess.graph.get_tensor_by_name(outputs[k].name)
                indiv_sig_data[tfconstants.OUTPUT_KEY_TO_TENSOR][k] = tensor
        self.set_tf1_model_attrs(sess, signature_tensor_mapping)
        return super().load()

    def predict(self, req_payload: Dict) -> Dict:
        """Single predict call"""
        return predict(req_payload, self.sess, self.sig_mapping)

    @staticmethod
    def get_verbs() -> List[str]:
        return [tfconstants.TfVerbs.PREDICT]


if __name__ == "__main__":
    from pathlib import Path
    import json
    import copy

    test_dir = Path(".").absolute() / "tests/remote_resources/"
    m = Tf1Model(str(test_dir / "models/tf1_models/inception/1"))
    t = m.load()
    with open(test_dir / "payloads/cat0_156kb_inception_tf1_col_request_body.json") as fh:
        data = json.load(fh)
    with open(test_dir / "payloads/cat0_156kb_inception_tf1_row_request_body.json") as fh:
        data2 = json.load(fh)

    req_payload = {
        "req_id_def": data,
        "ghi": copy.deepcopy(data),
        "456": {"naninainai": "123", "instances": "456"},
        "000": {"signature": "hello", "inputs": "123"},
        "789": {"signature_name": "predict_images", "inputs": "123"},
        "910": {"signature_name": "predict_images", "inputs": "123"},
        "1011": {"signature_name": "predict_images", "inputs": "123"},
        "abc": data2,
        "bbb": {"signature_name": "predict_images", "instances": [["abc"]]},
    }
    print(m.predict(req_payload))
