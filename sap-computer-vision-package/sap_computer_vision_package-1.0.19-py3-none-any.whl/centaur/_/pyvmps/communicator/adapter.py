from typing import Dict, Union, List

from centaur._.pyvmps.communicator.exceptions import MarshallException, SendMessageException, UnmarshallException
from centaur._.pyvmps.communicator.socket_base import SocketControl
from centaur._.pyvmps.communicator.utils import ujson_dumps_wrap, ujson_loads_wrap
from centaur._.pyvmps.cfg.config import GowebProtocolConst, PyvmpProtocol, SigTypes, EnvVarGoPyCommon, MessageType
from centaur._.pyvmps.logger.get_logger import get_logger
from centaur._.pyvmps.tracking.tracker import tracker
from centaur._.pyvmps.tracking.constants import Tracking
from centaur._.pyvmps.utils.common import current_milli_time

_logger = get_logger(__name__)
MsgId = str


class Adapter:
    """Adapter contains logic to covert messages received from the uds to pyvmp messages
    All layers above the adaptor should go through the adaptor to perform uds communication
    """

    def __init__(self, sc: SocketControl):
        self.sc = sc

    def send(self, pyvmp_msg: Dict, timeout: int = -1):
        """send wraps SocketControl send method. Performs unmarshalling from pyvmp msg to socket byte string

        NOTE: this method MAY block

        :param pyvmp_msg:
        :type pyvmp_msg: Dict
        """
        try:
            socket_msg: bytes = self.marshall(pyvmp_msg)
            self.sc.send(socket_msg, timeout)
        except SendMessageException:
            _logger.exception("Error sending payload")

    def receive(self, timeout: int = -1) -> Dict:
        """receive wraps socketControl's receive method.

        NOTE: This method WILL block if there is nothing sent by the connected socket

        :rtype: Dict
        """
        socket_msg: bytes = self.sc.receive(timeout)
        return self.unmarshall(socket_msg)

    @staticmethod
    def unmarshall(codec_and_full_msg: bytes) -> Dict[str, Dict]:
        """unmarshall converts socket_msg into 1 complete Pyvmp message

        :param socket_msg: byte string returned from SocketControl's receive method
        :type socket_msg: bytes
        :rtype: Dict

        New signal...unmarshall needs to produce a common template for pyvmp or whoever that calls it to process. This would allow new formats to be marshalled, yet handled without changing those components that call unmarshall.
        """
        recv_time = current_milli_time()
        pos = 0
        # TODO: Use codec len provided from go side
        codec_flag: int = codec_and_full_msg[0]
        full_msg = codec_and_full_msg[1:]
        socket_msg_len = len(full_msg)
        try:
            if codec_flag == GowebProtocolConst.PY_CODEC_TYPE_SIG_BYTES:
                try:
                    signal = SigTypes.byte_to_sig_mapping[full_msg]
                    return {GowebProtocolConst._PY_CODEC_SIGNAL_KEY: {PyvmpProtocol.MSG_TYPE: signal}}
                except KeyError:
                    _logger.exception("unrecognised signal")
                    raise
            msg_field_data_len: int = int(full_msg[pos : pos + GowebProtocolConst.PYVMP_JSON_STRUCTURE_LENGTH])
            pos += GowebProtocolConst.PYVMP_JSON_STRUCTURE_LENGTH
            indiv_msg_body: bytes = full_msg[pos : pos + msg_field_data_len]
            msg_field_data: Dict[MsgId, Dict] = ujson_loads_wrap(indiv_msg_body)
            if EnvVarGoPyCommon.ENABLE_HTTP_DEBUG:
                for _msg_id in msg_field_data.keys():
                    # insert anchor
                    # TODO: Decide to collect anyway, or based on __ENABLE_HTTP_DEBUG__ config
                    # only track for req type msg
                    if msg_field_data[_msg_id][PyvmpProtocol.MSG_TYPE] == MessageType.REQ.value:
                        tracker.create_entry(_msg_id)
                        tracker.insert_anchor(_msg_id, Tracking.PYVMP_RECEIVED_FULL_DATA.value, recv_time)

            pos += msg_field_data_len
            while pos < socket_msg_len:
                # read data
                data_length: int = int(full_msg[pos : pos + GowebProtocolConst.DATA_TO_READ_LENGTH])
                if data_length == 0:
                    break
                pos += GowebProtocolConst.DATA_TO_READ_LENGTH
                data_body: bytes = full_msg[pos : pos + data_length]
                len_msg_id = int(data_body[: GowebProtocolConst.MSG_ID_LENGTH])
                msg_id: str = data_body[
                    GowebProtocolConst.MSG_ID_LENGTH : GowebProtocolConst.MSG_ID_LENGTH + len_msg_id
                ].decode()
                actual_data: bytes = data_body[GowebProtocolConst.MSG_ID_LENGTH + len_msg_id :]
                pos += data_length
                msg_field_data[msg_id][PyvmpProtocol.DATA] = actual_data
                msg_field_data[msg_id][PyvmpProtocol.CODEC_FLAG] = codec_flag

            return msg_field_data
        except Exception as e:
            _logger.exception("adaptor|error_unmarshalling_socket_byte_string_to_pyvmp_msg")
            raise UnmarshallException from e

    @staticmethod
    def marshall(payload: Dict) -> bytes:
        """Converts pyvmp payload into byte string

        :param payload: Dict containing req_id to full pyvmp message
        :type payload: Dict
        :rtype: bytes
        """

        def determine_codec_type(msg: Dict) -> bytes:
            # condition for msg to be converted to signal:
            # msg_id is empty string and 1 key
            # inner dict has only MSG_TYPE as key
            if len(msg) == 1 and msg.get(GowebProtocolConst._PY_CODEC_SIGNAL_KEY):
                return GowebProtocolConst.PY_CODEC_SIGNAL
            return GowebProtocolConst.PY_CODEC_JSON

        def _construct_msg_json_struct_part(msg_json_struct: Dict) -> str:
            msg_json_struct_str: str = ujson_dumps_wrap(msg_json_struct)
            len_msg_json_struct_str: str = str(len(msg_json_struct_str)).zfill(
                GowebProtocolConst.PYVMP_JSON_STRUCTURE_LENGTH
            )
            return f"{len_msg_json_struct_str}{msg_json_struct_str}"

        def _construct_data_field_part(msg_id: bytes, data: bytes) -> bytes:
            data_len: int = len(data)
            msg_id_len: int = len(msg_id)
            msg_id_len_as_str: bytes = str(msg_id_len).zfill(GowebProtocolConst.MSG_ID_LENGTH).encode()
            total_len_as_str: bytes = (
                str(data_len + GowebProtocolConst.MSG_ID_LENGTH + msg_id_len)
                .zfill(GowebProtocolConst.DATA_TO_READ_LENGTH)
                .encode()
            )
            output_str: bytes = b"%s%s%s%s" % (total_len_as_str, msg_id_len_as_str, msg_id, data)
            return output_str

        codec: bytes = determine_codec_type(payload)
        if codec == GowebProtocolConst.PY_CODEC_SIGNAL:
            _logger.debug("marshall|signal")
            # payload = payload[next(iter(payload))]
            msg_type_dict: Dict = payload[GowebProtocolConst._PY_CODEC_SIGNAL_KEY]
            msg_type_int: int = msg_type_dict[PyvmpProtocol.MSG_TYPE]
            msg_type: bytes = SigTypes.sig_to_byte_mapping[msg_type_int]
            _logger.debug("marshall|msg_type=%s", msg_type)
            return b"%s%s" % (codec, msg_type)
        try:
            _logger.debug("marshall|regular message")
            msg_id_msg_json_struct: Dict[str, Dict] = {}
            data_segment: bytes = b""
            for msg_id, msg_body in payload.items():
                if msg_body.get(PyvmpProtocol.DATA):
                    # TODO: decide if there's a better place to call this function
                    data: Union[bytes, str, Dict] = msg_body.pop(PyvmpProtocol.DATA)
                    if isinstance(data, dict):
                        data = ujson_dumps_wrap(data)
                    if isinstance(data, str):
                        data = data.encode()
                    data_segment += _construct_data_field_part(msg_id.encode(), data)

                # tracker logic
                if EnvVarGoPyCommon.ENABLE_HTTP_DEBUG:
                    if (
                        msg_body[PyvmpProtocol.MSG_TYPE] == MessageType.RESP_OK.value
                        or msg_body[PyvmpProtocol.MSG_TYPE] == MessageType.RESP_ERR.value
                    ):
                        # only insert anchors for these 2 types of requests
                        _logger.debug("add timeline to msg_body")
                        tracker.insert_anchor(msg_id, Tracking.PYVMP_SEND_RES_START.value)
                        msg_body = insert_tracker_data(msg_id, msg_body)
                        tracker.pop_entry(msg_id)

                msg_id_msg_json_struct[msg_id] = msg_body
            msg_json_struct_segment: bytes = _construct_msg_json_struct_part(msg_id_msg_json_struct).encode()
            final_msg: bytes = codec + msg_json_struct_segment + data_segment
            return final_msg

        except Exception as e:
            _logger.exception("adaptor|error_marshalling_pyvmp_msg")
            raise MarshallException from e


def insert_tracker_data(msg_id: str, msg: Dict) -> Dict:
    """insert_into_msg adds RES_ATTRS into msg

    :param msg_id:
    :type msg_id: str
    :param msg:
    :type msg: Dict
    :rtype: Dict
    """
    anchors: List[int] = tracker.get_anchors(msg_id)
    if anchors:
        if PyvmpProtocol.RES_ATTRS in msg:
            msg[PyvmpProtocol.RES_ATTRS][PyvmpProtocol.TIMELINE_AFTER_UDS_OUT] = anchors
        else:
            msg[PyvmpProtocol.RES_ATTRS] = {PyvmpProtocol.TIMELINE_AFTER_UDS_OUT: anchors}
    _logger.debug("msg=%s", msg)
    return msg


if __name__ == "__main__":
    import shortuuid
    import copy

    sample = {
        shortuuid.uuid(): {"msg_type": 0, "data": b'{"something": "something else"}'},
        shortuuid.uuid(): {"msg_type": 2},
        shortuuid.uuid(): {"msg_type": 0, "data": b'{"something": "something else"}'},
    }
    print(sample)
    output = Adapter.marshall(copy.deepcopy(sample))
    print(output)
    sameple = Adapter.unmarshall(output)
    print(sample)
