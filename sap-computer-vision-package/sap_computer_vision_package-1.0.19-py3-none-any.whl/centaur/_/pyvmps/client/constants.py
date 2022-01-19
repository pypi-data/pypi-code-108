from centaur._.pyvmps.cfg.config import MessageType, PyvmpProtocol
from enum import Enum

# pylint: disable=pointless-string-statement
"""
Pyvmp message protocol:
{
  "msg_type": "INT_OF_MSG_TYPE",
  "__msg_type_corpus(explanatory field, for reference only, no need to be in a real message)": [
    "VMP_STARTUP_ERR(1)", "VMP_STARTUP_SUCCEEDED(2)",
    "HEALTH_CHECK(3)", "HEALTH_CHECK_OK(4)", "HEALTH_CHECK_ERR(5)",
    "RESP_OK(6)", "RESP_ERR(7)",
    "VMP_ASK_FOR_REQ(8)", "REQ(9)",
    "METRICS(10)",
    "M_RELOAD(11)", "M_OFFLOAD(12)", "M_LOAD(13)",
    "EXIT(14)", "VMP_EXIT_OK(15)", "VMP_EXIT_ERR(16)"
  ],
  "vmp_startup_succeeded_attrs": {
    "vmp_id": "INT_OF_VMP_ID",
  },
  "req_attrs": {
    "recv_ts": 1601626396029,
    "api_verb": "predict"
  },
  "metrics_attrs": {
    "name": "METRICS_NAME"
  },
  "m_reload_attrs": {},
  "m_offload_attrs": {},
  "m_load_attrs": {},
  "err": ["BYTES SLICE"],
  "data": ["BYTES SLICE"]
}
"""


class ModelType:
    """ModelType contains constants for supported model types"""

    TF = "tf"
    PYTHON = "py"
    PYTHON_WHEEL = "py_whl"

    @classmethod
    def all(cls):
        return [cls.TF, cls.PYTHON, cls.PYTHON_WHEEL]


class PyvmpStates:
    """PyvmpStates contain the different state constants that Pyvmp can hold"""

    INIT = "init"
    CONNECTED = "connected"
    MODEL_LOAD_FAILURE = "model_load_failure"
    MODEL_LOAD_SUCCESS = "model_load_success"


class PayloadKey:
    """PayloadKey contains constants used to describe action to take"""

    VERB: str = "api_verb"
    USR_DATA: str = "usr_data"


class PyvmpConstants:
    """PyvmpConstants."""

    INTERVAL = 60  # health reporter interval


class MessageConstants:
    """MessageConstants."""

    ASK_FOR_WORK = {PyvmpProtocol.MSG_TYPE: MessageType.VMP_ASK_FOR_REQ.value}
    HEARTBEAT = {PyvmpProtocol.MSG_TYPE: MessageType.HEARTBEAT.value}
    HEALTH_CHECK_OK = {PyvmpProtocol.MSG_TYPE: MessageType.HEALTH_CHECK_OK.value}
    EXIT_OK = {PyvmpProtocol.MSG_TYPE: MessageType.VMP_EXIT_OK.value}


Tracking = Enum(
    "Tracking", ["PYVMP_START_INF", "PYVMP_UNWRAP_BYTES", "PYVMP_PREDICT_DONE", "PYVMP_WRAP_DICT"], start=0
)  # type: ignore
