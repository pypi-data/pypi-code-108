"""
Info needed:
1) path to model
2) model type (tf? tf2? python? etc)
3) uds_address
"""
import sys
import copy
import pydoc
import traceback

from collections import defaultdict
from typing import Dict, List, Optional, Union, NamedTuple, Callable, Any, Tuple

from centaur import constants as public_constants
from centaur._.pyvmps.cfg import constants
from centaur._.pyvmps.client.constants import ModelType, PayloadKey
from centaur._.pyvmps.client.exceptions import ModelNotLoadedException
from centaur._.pyvmps.client.usr_payload_parser import parse_usr_payload, ParsedUsrPayload
from centaur._.pyvmps.client.utils import construct_res_err_message, construct_res_ok_message
from centaur._.pyvmps.models.base_model import Model
from centaur._.pyvmps.cfg.versioned_model import _VersionedModel
from centaur._.pyvmps.communicator.utils import ujson_dumps_wrap
from centaur._.pyvmps.cfg.config import EnvVarGoPyCommon, PyvmpProtocol
from centaur._.pyvmps.error_handling.constants import ErrorResponseKeys as ek
from centaur._.pyvmps.error_handling.errors import (
    invalid_input,
    model_output_not_json_serializable,
    failed_to_call_pre_processor,
    failed_to_call_post_processor,
    invalid_return_from_pre_processor,
    invalid_return_from_post_processor,
)
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.utils.common import current_milli_time
from centaur._.pyvmps.tracking.tracker import tracker
from centaur._.pyvmps.tracking.constants import Tracking

_logger = get_logger(__name__)


def _get_model(vm: _VersionedModel) -> Model:
    model_type = vm.model_type
    if model_type == ModelType.TF:
        import tensorflow as tf

        if tf.__version__.split(".")[0] == "1":
            from centaur._.pyvmps.client.pyvmp_models.tf1 import Tf1ModelPyvmp

            return Tf1ModelPyvmp(vm.model_path)

        if tf.__version__.split(".")[0] == "2":
            from centaur._.pyvmps.client.pyvmp_models.tf2 import Tf2ModelPyvmp

            return Tf2ModelPyvmp(vm.model_path)
    elif model_type == ModelType.PYTHON:
        from centaur._.pyvmps.client.pyvmp_models.python import PymodelPyvmp

        return PymodelPyvmp(
            vm.model_path, vm.py_model_interface_filepath, vm.py_model_interface_class_name, vm.py_model_init_params
        )

    elif model_type == ModelType.PYTHON_WHEEL:
        from centaur._.pyvmps.client.pyvmp_models.python_whl import PythonWheel

        return PythonWheel(vm.py_whl_model_interface_import_path, vm.model_path, vm.py_model_init_params)


class _PrePostProcessors(NamedTuple):
    # fmt: off

    # def pre_processor(payload, **kwargs)
    #     return pre_processed_payload, kwargs
    pre: Callable[
            [Union[dict, list, bytes], Any],
            Tuple[
                Any, Optional[Dict[str, Any]]
            ]
        ] = None

    # def post_processor(model_output, **kwargs)
    #     return post_processed_model_output, dict_of_response_header
    post: Callable[
            [Any, Any],
            Tuple[
                Union[dict, list, bytes], Optional[Dict[str, str]]
            ]
        ] = None
    # fmt: on


def _get_pre_post_processors(vm: _VersionedModel) -> _PrePostProcessors:
    def _(import_path: List[str]) -> Callable:
        if not import_path:
            return None

        tmp, obj = import_path[0], None

        if len(import_path) == 2:
            tmp = import_path[1]
            if import_path[0] not in sys.path:
                obj = pydoc.locate(tmp)
                if obj:
                    raise ValueError(
                        "configured pre-/post- function import path: '{}' conflicts with existing modules in the env"
                    )
                sys.path.append(import_path[0])

        obj = pydoc.locate(tmp)
        if callable(obj):
            return obj

        raise ValueError(
            "configured pre-/post- function import path: '{}' doesn't point to any callable object".format(import_path)
        )

    return _PrePostProcessors(pre=_(vm.py_pre_proc_func_import_path), post=_(vm.py_post_proc_func_import_path))


class ModelController:
    """PyVmp contains business logic to manage model lifecycle and communication with main engine"""

    def __init__(self, vm: _VersionedModel):
        self.vm = vm
        self.model_loaded = False

    def load_model(self) -> List[str]:
        """load_model and return verb_list

        :rtype: List[str]
        """
        self.model = _get_model(self.vm)

        try:
            self.model_loaded = self.model.load_w_psutil(self.vm.target_cpus, self.vm.trailing_cpus)

            self.pre_processor, self.post_processor = _get_pre_post_processors(self.vm)

            return list(self.model.get_verbs())

        except Exception as e:
            _logger.exception("error loading model")
            raise e

    def service_request(self, req_id_pyvmpmsg_body: Dict[str, Dict]) -> Dict:
        """service_request will pass http-request body to model to perform actual prediction.
        req_id_msg_body looks like this
        {
            "req_id": "MSG_BODY"
        }
        It returns the fully constructed message with the MSG type set as well

        :param req_id_to_pyvmp_msg:
        :type req_id_to_pyvmp_msg: Dict[str, Dict]
        """

        if not self.model_loaded:
            raise ModelNotLoadedException("Model has not yet been loaded, cannot perform inference")

        _logger.info("service_request,batch_size=%s", len(req_id_pyvmpmsg_body))

        parsed_usr_payloads: Dict[str, Any] = {}
        pre_processed_usr_payloads: Dict[str, Any] = defaultdict(dict)
        batch_inference_payload: Dict[str, Dict] = {}
        pyvmp_response: Dict[str, Dict] = {}
        errs_before_calling_predict: Dict[str, Dict] = {}
        results: Dict[str, Dict] = {}
        errs: Dict[str, Dict] = {}

        for req_id, pyvmp_msg in req_id_pyvmpmsg_body.items():
            req_attrs: Optional[Dict] = pyvmp_msg.get(PyvmpProtocol.REQ_ATTRS)
            if not req_attrs:
                _logger.warning("missing request attrs")
                errs_before_calling_predict[req_id] = invalid_input.generate_error()
                continue

            timestamp = req_attrs.get(PyvmpProtocol.RECV_TS)
            if timestamp:
                now = int(current_milli_time())
                if now - timestamp > EnvVarGoPyCommon.TIMEOUT:
                    _logger.info("timeout exceeded, discarding req_id=%s", req_id)
                    continue

            try:
                pup: ParsedUsrPayload = parse_usr_payload(
                    pyvmp_msg[PyvmpProtocol.DATA], req_attrs.get(PyvmpProtocol.CONTENT_TYPE, [])
                )

                parsed_usr_payloads[req_id] = pup

                parsed_usr_payload = pup.payload
                parsed_usr_payload_content_types = {
                    public_constants.KwargsKeys.orig_parsed_usr_payload_content_types: pup.content_types
                }
                pre_processed_usr_payload, pre_processed_kwargs = parsed_usr_payload, {}

                if self.pre_processor:
                    try:
                        pre_processed_data = self.pre_processor(
                            copy.deepcopy(parsed_usr_payload), **parsed_usr_payload_content_types
                        )
                    except Exception as e:
                        _logger.debug(traceback.format_exc)
                        errs_before_calling_predict[req_id] = failed_to_call_pre_processor.generate_error(
                            details=repr(e)
                        )
                        continue

                    if not pre_processed_data:
                        errs_before_calling_predict[req_id] = invalid_return_from_pre_processor.generate_error(
                            details="'None' return from model pre-processor"
                        )
                        continue

                    if isinstance(pre_processed_data, tuple):
                        if len(pre_processed_data) == 1:
                            pre_processed_usr_payload = pre_processed_data[0]
                        elif len(pre_processed_data) == 2:
                            pre_processed_usr_payload, pre_processed_kwargs = pre_processed_data
                        else:
                            errs_before_calling_predict[req_id] = invalid_return_from_pre_processor.generate_error(
                                details="more than 2 returns from model pre-processor"
                            )
                            continue
                    else:
                        pre_processed_usr_payload = pre_processed_data

                    # Explicitly revoked by the pre-processor, lets respect it.
                    if not pre_processed_kwargs:
                        pre_processed_kwargs = {}

                    if not isinstance(pre_processed_kwargs, dict):
                        errs_before_calling_predict[req_id] = invalid_return_from_pre_processor.generate_error(
                            details="second return from model pre-processor must be a dict"
                        )
                        continue

                    pre_processed_usr_payloads[req_id] = {
                        public_constants.KwargsKeys.pre_processed_usr_payload: pre_processed_usr_payload,
                        public_constants.KwargsKeys.pre_processed_kwargs: pre_processed_kwargs,
                    }

                tracker.insert_anchor(req_id, Tracking.PYVMP_UNWRAPPED_BYTES.value)

                # include req_attrs and data body in batch_inference_payload
                batch_inference_payload[req_id] = {
                    PayloadKey.USR_DATA: pre_processed_usr_payload,
                    **pyvmp_msg[PyvmpProtocol.REQ_ATTRS],
                    constants.KWARGS: pre_processed_kwargs if self.pre_processor else parsed_usr_payload_content_types,
                }
            except Exception as e:
                _logger.debug(traceback.format_exc())
                errs_before_calling_predict[req_id] = invalid_input.generate_error(details=repr(e))

        if len(batch_inference_payload) == 1:  # if no batching, can just call single predict
            results, errs = self.model._single_predict(batch_inference_payload)
        elif len(batch_inference_payload) > 1:
            results, errs = self.model._batch_predict(batch_inference_payload)

        for req_id, model_output in results.items():
            post_processed_model_output = model_output
            model_output_types: dict = {}

            if self.post_processor:
                try:
                    pup = parsed_usr_payloads[req_id]
                    post_processed_data = self.post_processor(
                        model_output,
                        **{
                            public_constants.KwargsKeys.orig_parsed_usr_payload: pup.payload,
                            public_constants.KwargsKeys.orig_parsed_usr_payload_content_types: pup.content_types,
                            **pre_processed_usr_payloads[req_id],
                        }
                    )
                except Exception as e:
                    _logger.debug(traceback.format_exc())
                    errs[req_id] = failed_to_call_post_processor.generate_error(details=repr(e))
                    continue

                if not post_processed_data:
                    errs[req_id] = invalid_return_from_post_processor.generate_error(
                        details="None return from model post-processor"
                    )
                    continue

                if isinstance(post_processed_data, tuple):
                    if len(post_processed_data) == 1:
                        post_processed_model_output = post_processed_data[0]
                    elif len(post_processed_data) == 2:
                        post_processed_model_output, model_output_types = post_processed_data
                    else:
                        errs[req_id] = invalid_return_from_post_processor.generate_error(
                            details="more than 2 returns from model post-processor"
                        )
                        continue
                else:
                    post_processed_model_output = post_processed_data

                if not isinstance(model_output_types, dict):
                    errs[req_id] = invalid_return_from_post_processor.generate_error(
                        details="second return from model post-processor must be a dict"
                    )
                    continue

                found_err = False
                for k, v in model_output_types.items():
                    if not isinstance(k, str) or not isinstance(v, str):
                        errs[req_id] = invalid_return_from_post_processor.generate_error(
                            details="second return from model post-processor must be type: `dict[str, str]`, pls report your use case if it cannot be fulfilled"
                        )
                        found_err = True
                        break

                if found_err:
                    continue

            if not isinstance(post_processed_model_output, bytes):
                try:
                    post_processed_model_output: bytes = ujson_dumps_wrap(post_processed_model_output)
                except Exception as e:
                    _logger.debug("error serializing json, details=%s", traceback.format_exc())
                    errs[req_id] = model_output_not_json_serializable.generate_error(details=repr(e))
                    continue
            else:
                if not model_output_types:
                    model_output_types = {public_constants.CONTENT_TYPE: "application/octet-stream"}

            # For now lets allow 'Content-Type' only.
            if model_output_types and model_output_types.get(public_constants.CONTENT_TYPE, ""):
                model_output_types = {public_constants.CONTENT_TYPE: model_output_types[public_constants.CONTENT_TYPE]}
            else:
                model_output_types = {}

            pyvmp_response[req_id] = construct_res_ok_message(post_processed_model_output, res_attrs=model_output_types)

            tracker.insert_anchor(req_id, Tracking.PYVMP_WRAPPED_DICT.value)

        errs = {**errs, **errs_before_calling_predict}

        for req_id, model_output in errs.items():
            model_output_err: bytes = ujson_dumps_wrap(model_output[ek.ERROR])
            tracker.insert_anchor(req_id, Tracking.PYVMP_WRAPPED_DICT.value)
            pyvmp_response[req_id] = construct_res_err_message(model_output_err)

        return pyvmp_response
