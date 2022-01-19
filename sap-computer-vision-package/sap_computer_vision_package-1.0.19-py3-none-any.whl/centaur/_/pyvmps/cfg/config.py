# mypy: ignore-errors
import enum
from typing import Dict

from environs import Env

_env = Env()


class _EnvConst:
    """_EnvConst stores all the env var set by the go component"""

    PY_LOG_LEVEL = "VMP_LOG_LEVEL"
    PY_REQ_TIMEOUT_MILLIS = "VMP_REQ_TIMEOUT_MILLIS"
    PY_UDS_SOCK_FILEPATH = "VMP_UDS_SOCK_FILEPATH"
    PY_DIVIDER_COMMA = "VMP_DIVIDER_COMMA"

    PY_MSG_TYPE = "VMP_MSG_TYPE"
    PY_VMP_STARTUP_OK_ATTRS = "VMP_VMP_STARTUP_OK_ATTRS"
    PY_VMP_STARTUP_ERR_ATTRS = "VMP_VMP_STARTUP_ERR_ATTRS"
    PY_REQ_ATTRS = "VMP_REQ_ATTRS"
    PY_RES_ATTRS = "VMP_RES_ATTRS"
    PY_VMP_ID = "VMP_ID"
    PY_API_VERBS = "VMP_API_VERBS"
    PY_RECV_TS = "VMP_RECV_TS"
    PY_VERB = "VMP_API_VERB"
    PY_CONTENT_TYPE = "VMP_CONTENT_TYPE"

    # protocol constants
    PY_LEN_PKT_HEADER_BYTES = "VMP_LEN_PKT_HEADER_BYTES"
    PY_LEN_IS_LAST_PKT_FLAG_BYTES = "VMP_LEN_IS_LAST_PKT_FLAG_BYTES"
    PY_LEN_JSON_STRUCT_BYTES = "VMP_LEN_JSON_STRUCT_HEADER_BYTES"
    PY_LEN_PAYLOAD_BYTES = "VMP_LEN_PAYLOAD_HEADER_BYTES"
    PY_LEN_MSG_ID_BYTES = "VMP_LEN_MSG_ID_HEADER_BYTES"
    PY_LEN_CODEC_TYPE_BYTES = "VMP_LEN_CODEC_TYPE_BYTES"

    PY_LAST_PKT_FLAG = "VMP_IS_LAST_PKT_FLAG_YES"
    PY_NOT_LAST_PKT_FLAG = "VMP_IS_LAST_PKT_FLAG_NO"
    PY_CODEC_TYPE_SIG_BYTES = "VMP_CODEC_TYPE_SIG_BYTES"
    PY_CODEC_TYPE_JSON_STRUCT_BYTES = "VMP_CODEC_TYPE_JSON_STRUCT_BYTES"

    ALL_MODEL_TYPES = "VMP_ALL_MODEL_TYPES"
    ALL_SUPPORTED_HTTP_CODECS = "VMP_ALL_SUPPORTED_HTTP_CODECS"
    ALL_MSG_TYPES_BYTES = "VMP_ALL_MSG_TYPES_BYTES"
    ALL_MSG_TYPES = "VMP_ALL_MSG_TYPES"

    ENABLE_HTTP_DEBUG = "__ENABLE_HTTP_DEBUG__"
    PY_TIMELINE_AFTER_UDS_OUT = "VMP_TIMELINE"


class SupportedHTTPCodecs:
    _codecs = enum.Enum(
        "_codecs",
        _env.dict(
            _EnvConst.ALL_SUPPORTED_HTTP_CODECS,
            {
                "JSON": "application/json",
                "NPY": "python/npy",
                "NPZ": "python/npz",
                "PD_FEATHER": "python/pd_feather",
                "PD_PARQUET": "python/pd_parquet",
            },
        ),
    )

    JSON = _codecs.JSON
    NPY = _codecs.NPY
    NPZ = _codecs.NPZ
    PD_FEATHER = _codecs.PD_FEATHER
    PD_PARQUET = _codecs.PD_PARQUET


class EnvVarGoPyCommon:
    """For all environment variables in this class, its value will be set by the go main engine
    Default value here is only for developer to conveniently test the 'pyvmps' part standalone locally
    - without the need to run the go main engine.
    """

    # DEBUG INFO WARNING ERROR CRITICAL
    LOG_LEVEL = _env.str(_EnvConst.PY_LOG_LEVEL, "WARNING")
    TIMEOUT = _env.int(_EnvConst.PY_REQ_TIMEOUT_MILLIS, 10)
    UDS_ADDRESS = _env.str(_EnvConst.PY_UDS_SOCK_FILEPATH, "/tmp/centaur.sock")
    DIVIDER_COMMA = _env.str(_EnvConst.PY_DIVIDER_COMMA, ",")
    ENABLE_HTTP_DEBUG = _env.bool(_EnvConst.ENABLE_HTTP_DEBUG, False)


class PyvmpProtocol:
    """Refer to keywords used in payloads"""

    MSG_TYPE = _env.str(_EnvConst.PY_MSG_TYPE, "msg_type")
    VMP_STARTUP_OK_ATTRS = _env.str(_EnvConst.PY_VMP_STARTUP_OK_ATTRS, "vmp_startup_ok_attrs")
    VMP_STARTUP_ERR_ATTRS = _env.str(_EnvConst.PY_VMP_STARTUP_ERR_ATTRS, "vmp_startup_err_attrs")
    REQ_ATTRS = _env.str(_EnvConst.PY_REQ_ATTRS, "req_attrs")
    RES_ATTRS = _env.str(_EnvConst.PY_RES_ATTRS, "res_attrs")
    TIMELINE_AFTER_UDS_OUT = _env.str(_EnvConst.PY_TIMELINE_AFTER_UDS_OUT, "timeline")
    MSG_TYPE_DICT: Dict[str, str] = _env.dict(
        _EnvConst.ALL_MSG_TYPES,
        {
            "SIG_OK": 1,
            "VMP_STARTUP_OK": 2,
            "VMP_STARTUP_ERR": 3,
            "SIG_HEALTH_CHECK": 4,
            "SIG_HEALTH_CHECK_OK": 5,
            "HEALTH_CHECK_ERR": 6,
            "SIG_VMP_ASK_FOR_REQ": 7,
            "REQ": 8,
            "RESP_OK": 9,
            "RESP_ERR": 10,
            "SIG_EXIT": 11,
            "SIG_VMP_EXIT_OK": 12,
            "SIG_HEART_BEAT": 13,
        },
        subcast_values=int,
    )
    # Note:
    #   For `SIG_BYTES_DICT` key as str is intended, although `_env` supports `subcast_keys`.
    SIG_BYTES_DICT = _env.dict(
        _EnvConst.ALL_MSG_TYPES_BYTES,
        {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "9": 9,
            "10": 10,
            "1": 1,
            "8": 8,
            "11": 11,
            "12": 12,
            "13": 13,
            "7": 7,
        },
        subcast_values=int,
    )
    VMP_ID = _env.str(_EnvConst.PY_VMP_ID, "vmp_id")
    API_VERBS = _env.str(_EnvConst.PY_API_VERBS, "api_verbs")
    RECV_TS = _env.str(_EnvConst.PY_RECV_TS, "recv_ts")
    VERB = _env.str(_EnvConst.PY_VERB, "api_verb")
    CONTENT_TYPE = _env.str(_EnvConst.PY_CONTENT_TYPE, "content_type")
    DATA = "data"
    CODEC_FLAG = "codec_flag"


# pylint: disable=no-member
class MessageType(enum.Enum):
    """MessageType contains name & values of msg_type in the pyvmp message protocol"""

    _msg = enum.Enum("MessageType", PyvmpProtocol.MSG_TYPE_DICT)  # type: ignore
    SIG_OK = _msg.SIG_OK.value
    VMP_STARTUP_SUCCEEDED = _msg.VMP_STARTUP_OK.value
    VMP_STARTUP_ERR = _msg.VMP_STARTUP_ERR.value
    HEALTH_CHECK = _msg.SIG_HEALTH_CHECK.value
    HEALTH_CHECK_OK = _msg.SIG_HEALTH_CHECK_OK.value
    HEALTH_CHECK_ERR = _msg.HEALTH_CHECK_ERR.value
    VMP_ASK_FOR_REQ = _msg.SIG_VMP_ASK_FOR_REQ.value
    REQ = _msg.REQ.value
    RESP_OK = _msg.RESP_OK.value
    RESP_ERR = _msg.RESP_ERR.value
    EXIT = _msg.SIG_EXIT.value
    VMP_EXIT_OK = _msg.SIG_VMP_EXIT_OK.value
    HEARTBEAT = _msg.SIG_HEART_BEAT.value

    @classmethod
    def details(cls):
        print(list(cls._msg.value))
        print([v for v in vars(cls) if not v.startswith("__")])


class SigTypes:
    """SigTypes contain mapping between signal msg type int to byte representation"""

    sig_to_byte_mapping: Dict[int, bytes] = {int(k): bytes([v]) for k, v in PyvmpProtocol.SIG_BYTES_DICT.items()}
    byte_to_sig_mapping: Dict[bytes, int] = {bytes([v]): int(k) for k, v in PyvmpProtocol.SIG_BYTES_DICT.items()}

    @classmethod
    def details(cls):
        print("sig_to_byte_mapping={}".format(cls.sig_to_byte_mapping))
        print("byte_to_sig_mapping={}".format(cls.byte_to_sig_mapping))


class GowebProtocolConst:
    """GowebProtocolConst contain values related to the protocol used to pass data between pyvmp and goweb"""

    MSG_HEADER_LENGTH = _env.int(_EnvConst.PY_LEN_PKT_HEADER_BYTES, 9)
    X_OF_PARTS_LENGTH = _env.int(_EnvConst.PY_LEN_IS_LAST_PKT_FLAG_BYTES, 1)
    PYVMP_JSON_STRUCTURE_LENGTH = _env.int(_EnvConst.PY_LEN_JSON_STRUCT_BYTES, 6)
    DATA_TO_READ_LENGTH = _env.int(_EnvConst.PY_LEN_PAYLOAD_BYTES, 9)
    MSG_ID_LENGTH = _env.int(_EnvConst.PY_LEN_MSG_ID_BYTES, 3)

    PY_LAST_PKT_FLAG: bytes = _env.str(_EnvConst.PY_LAST_PKT_FLAG, "0").encode()
    PY_NOT_LAST_PKT_FLAG: bytes = _env.str(_EnvConst.PY_NOT_LAST_PKT_FLAG, "1").encode()
    _PY_LAST_PKT_FLAG: bytes = bytes([int(PY_LAST_PKT_FLAG)])
    _PY_NOT_LAST_PKT_FLAG: bytes = bytes([int(PY_NOT_LAST_PKT_FLAG)])

    # NOTE: Go will set codec type as list with 1 element
    # Read as list
    _PY_CODEC_TYPE_SIG_BYTES: str = _env.str(_EnvConst.PY_CODEC_TYPE_SIG_BYTES, "0")
    _PY_CODEC_TYPE_JSON_STRUCT_BYTES: str = _env.str(_EnvConst.PY_CODEC_TYPE_JSON_STRUCT_BYTES, "1")
    _PY_CODEC_TYPE_LEN_BYTES: str = _env.str(_EnvConst.PY_LEN_CODEC_TYPE_BYTES, "1")

    # Extract integer value from list
    PY_CODEC_TYPE_SIG_BYTES: int = int(_PY_CODEC_TYPE_SIG_BYTES)
    PY_CODEC_TYPE_JSON_STRUCT_BYTES: int = int(_PY_CODEC_TYPE_JSON_STRUCT_BYTES)
    PY_CODEC_TYPE_LEN_BYTES: int = int(_PY_CODEC_TYPE_LEN_BYTES)

    # Convert to bytes \x00 and \x01 to use when sending back to goweb
    PY_CODEC_SIGNAL: bytes = bytes([PY_CODEC_TYPE_SIG_BYTES])
    PY_CODEC_JSON: bytes = bytes([PY_CODEC_TYPE_JSON_STRUCT_BYTES])

    # Constants not set by env var
    _PY_CODEC_SIGNAL_KEY: str = ""
