import binascii
import copy
from typing import Callable, Dict, List, Optional, Tuple
import tensorflow as tf

from centaur._.pyvmps.client.pyvmp_models._tf_helper import batch_deconstruct
from centaur._.pyvmps.client.utils import unpack_and_check_verb
from centaur._.pyvmps.error_handling.constants import ExceptionMsgs as em
from centaur._.pyvmps.error_handling.errors import invalid_input  # internal_error,
from centaur._.pyvmps.error_handling.errors import invalid_tensor_input, invalid_tensor_signature, tf_graph_error
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.models.base_model import BatchedModel
from centaur._.pyvmps.models.centaur_model import CentaurModelMixin
from centaur._.pyvmps.models.exceptions import (
    InvalidInputException,
    InvalidInputTensorShape,
    InvalidSignatureKeyException,
    ModelPredictErrorException,
)
from centaur._.pyvmps.models.tf import constants as tfconstants
from centaur._.pyvmps.models.tf.constants import TfVerbs, SigTensorInfo
from centaur._.pyvmps.models.tf.tf2.model import Tf2Model
from centaur._.pyvmps.models.tf.tf2.payload_utils import (
    tf2_col_format_create_input_tensors,
    tf2_col_format_handle_result,
    tf2_row_format_create_input_tensors,
    tf2_row_format_handle_result,
)
from centaur._.pyvmps.models.tf.utils import col_format_preprocess_data, row_format_preprocess_data
from centaur._.pyvmps.tracking.tracker import tracker
from centaur._.pyvmps.tracking.constants import Tracking
from centaur._.pyvmps.utils.common import current_milli_time

BatchedSigDict = Dict

_logger = get_logger(__file__)

row_format_funcs = [row_format_preprocess_data, tf2_row_format_create_input_tensors, tf2_row_format_handle_result]
col_format_funcs = [col_format_preprocess_data, tf2_col_format_create_input_tensors, tf2_col_format_handle_result]

# NOTE: Temp setting of tf verbs since only predict is supported
tf_predict_set = set([TfVerbs.PREDICT])


def _construct_batch_tuple_lists(req_id: str, batched_payload: Dict) -> Tuple[str, str, Callable, Callable]:
    req_payload, _ = unpack_and_check_verb(batched_payload, tf_predict_set)
    sig: str = req_payload.get(tfconstants.SIGNATURE_NAME, tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY)
    payload_partial_func, output_formatter = batch_deconstruct(req_payload, row_format_funcs, col_format_funcs)
    return req_id, sig, payload_partial_func, output_formatter


def _construct_batch_ds(
    sig_tensor_dict: Dict,
    batch_data_store: Dict,
    req_id: str,
    sig: str,
    partial_extract_func: Callable,
    output_formatter_func: Callable,
):
    sig_tensor_info: Optional[SigTensorInfo] = sig_tensor_dict.get(sig, None)
    if not sig_tensor_info:
        raise InvalidSignatureKeyException(em.TF_INVALID_SIGNATURE_KEY.format(signature=sig))

    # Convert http request body to tensor-object data mapping
    payload_input_data_dict = partial_extract_func(indiv_sig_data=sig_tensor_info)

    if sig not in batch_data_store:
        batch_data_store[sig] = {
            tfconstants.CONC_FUNC: sig_tensor_info.conc_func,
            tfconstants.MERGED_INPUT_TENSORS: {
                input_key: tf.concat([tf_constant_value], axis=0)
                for input_key, tf_constant_value in payload_input_data_dict.items()
            },
            tfconstants.OUTPUT_FORMATTER_REQ_ID_MAPPER: [
                tfconstants.TfMergedRequestsTuple(
                    req_id, 0, len(payload_input_data_dict[next(iter(payload_input_data_dict))]), output_formatter_func
                )
            ],
        }
    else:
        for (input_key, tf_constant_value) in payload_input_data_dict.items():
            batch_data_store[sig][tfconstants.MERGED_INPUT_TENSORS][input_key] = tf.concat(
                [batch_data_store[sig][tfconstants.MERGED_INPUT_TENSORS][input_key], tf_constant_value], axis=0
            )
        next_start_idx = batch_data_store[sig][tfconstants.OUTPUT_FORMATTER_REQ_ID_MAPPER][-1].end_index
        batch_data_store[sig][tfconstants.OUTPUT_FORMATTER_REQ_ID_MAPPER].append(
            tfconstants.TfMergedRequestsTuple(
                req_id,
                next_start_idx,
                next_start_idx + len(payload_input_data_dict[next(iter(payload_input_data_dict))]),
                output_formatter_func,
            )
        )
        _logger.debug(
            "output_formatter_added=%s", batch_data_store[sig][tfconstants.OUTPUT_FORMATTER_REQ_ID_MAPPER][-1]
        )


def _inner_predict_func(
    batch_err_store: Dict,
    conc_func: Callable,
    merged_input_tensors,
    output_formatter_req_id_mapper: List[tfconstants.TfMergedRequestsTuple],
) -> Dict:
    """fetches: Dict[str, tf.Tensor] - output key to tensor dict
    feed_dict: input tensor to payload dict

    """
    formatted_outputs = dict()
    try:
        outputs: Dict = conc_func(**merged_input_tensors)
        ts = current_milli_time()

        for x in output_formatter_req_id_mapper:
            temp = copy.copy(outputs)
            for k, v in temp.items():
                temp[k] = v[x.start_index : x.end_index]
            formatted_outputs[x.req_id] = x.formatter(temp)
            tracker.insert_anchor(x.req_id, Tracking.PYVMP_PREDICT_DONE.value, ts)

    except Exception:
        _logger.info("error encountered during batch predict")
        for tf_merged_request_tuple in output_formatter_req_id_mapper:
            indiv_input_tensors = {
                k: v[tf_merged_request_tuple.start_index : tf_merged_request_tuple.end_index]
                for k, v in merged_input_tensors.items()
            }
            try:
                indiv_outputs = conc_func(**indiv_input_tensors)
                formatted_outputs[tf_merged_request_tuple.req_id] = tf_merged_request_tuple.formatter(indiv_outputs)
            except Exception as e:
                _logger.info("error_for_single_predict|req_id=%s", tf_merged_request_tuple.req_id)
                _logger.debug(str(e))
                batch_err_store[tf_merged_request_tuple.req_id] = tf_graph_error.generate_error(details=repr(e))
            finally:
                tracker.insert_anchor(tf_merged_request_tuple.req_id, Tracking.PYVMP_PREDICT_DONE.value)
    return formatted_outputs


def tf2_batch_predict(
    batch_payload: Dict[str, Dict], sig_tensor_dict: Dict[str, Dict]
) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    batch_data_store: Dict[str, BatchedSigDict] = {}
    batch_err_store: Dict = {}
    model_output: Dict = {}

    # RETURN FORMATTED_OUTPUTS

    for req_id, req_payload in batch_payload.items():
        try:
            _construct_batch_ds(sig_tensor_dict, batch_data_store, *_construct_batch_tuple_lists(req_id, req_payload))
        except (InvalidInputException, InvalidInputTensorShape) as e:
            batch_err_store[req_id] = invalid_tensor_input.generate_error(details=repr(e))
        except InvalidSignatureKeyException as e:
            batch_err_store[req_id] = invalid_tensor_signature.generate_error(details=repr(e))
        except binascii.Error as e:
            batch_err_store[req_id] = invalid_input.generate_error(details=repr(e))
        except Exception as e:
            _logger.exception("unhandled_exeception_caught")
            batch_err_store[req_id] = invalid_input.generate_error(details=repr(e))
    for _, tensor_tuple in batch_data_store.items():
        try:
            model_output = {**model_output, **_inner_predict_func(batch_err_store, *tensor_tuple.values())}
        except Exception:
            _logger.exception("predict_func|unknown_error")
    return model_output, batch_err_store


class Tf2ModelPyvmp(Tf2Model, BatchedModel, CentaurModelMixin):
    """Model class with pyvmp logic embedded"""

    def _single_predict(self, single_req_payload: Dict[str, Dict]) -> Tuple[Dict, Dict]:
        req_id = next(iter(single_req_payload))
        batch_payload = single_req_payload[req_id]
        payload, _ = unpack_and_check_verb(batch_payload, [TfVerbs.PREDICT])
        result_payload = {}
        errs = {}
        try:
            output = super().predict(payload)
            result_payload[req_id] = output
        except (InvalidInputException, InvalidInputTensorShape) as e:
            errs[req_id] = invalid_tensor_input.generate_error(details=repr(e))
        except InvalidSignatureKeyException as e:
            errs[req_id] = invalid_tensor_signature.generate_error(details=repr(e))
        except binascii.Error as e:
            errs[req_id] = invalid_input.generate_error(details=repr(e))
        except ModelPredictErrorException as e:
            errs[req_id] = invalid_input.generate_error(details=repr(e))
        except Exception as e:
            errs[req_id] = invalid_input.generate_error(details=repr(e))
        finally:
            tracker.insert_anchor(req_id, Tracking.PYVMP_PREDICT_DONE.value)
        return result_payload, errs

    def _batch_predict(self, batched_req_dict: Dict[str, Dict]) -> Tuple[Dict, Dict]:
        """To be used by pyvmp to handle http-request level batched payload. Returns 2 dicts, model_outputs and batched_errs
        model_outputs stores successful model results
        batched_errs store errs.
        Both dicts use req_id as keys, where union(model_outputs.keys(), batched_errs.keys()) === batched_req_dict.keys()

        :param batched_req_dict: Dict with req_id as key, http-request body as values
        :type batched_req_dict: Dict[str, Dict]
        :rtype: Tuple[Dict, Dict]
        """
        return tf2_batch_predict(batched_req_dict, self.sig_tensor_dict)
