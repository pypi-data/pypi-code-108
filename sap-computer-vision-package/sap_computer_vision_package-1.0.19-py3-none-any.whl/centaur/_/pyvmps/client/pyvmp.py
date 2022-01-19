import time
import shortuuid

from threading import Event, Thread
from typing import Dict, List, Tuple

from centaur._.pyvmps.client.constants import PyvmpConstants, PyvmpStates, MessageConstants
from centaur._.pyvmps.client.exceptions import UnexpectedMessageException
from centaur._.pyvmps.client.utils import construct_err_reg_msg, construct_reg_msg
from centaur._.pyvmps.communicator.adapter import Adapter
from centaur._.pyvmps.cfg.config import GowebProtocolConst, MessageType, PyvmpProtocol
from centaur._.pyvmps.error_handling.constants import ErrorResponseKeys as ek
from centaur._.pyvmps.error_handling.errors import model_loading_error
from centaur._.pyvmps.logger.get_logger import get_logger

_logger = get_logger(__name__)


class PyVmp:
    """PyVmp performs model loading, registration, serving of request and
    other business logic
    """

    def __init__(self, vmp_id: int, adapter: Adapter, model_controller):
        self.adapter = adapter
        self.mc = model_controller
        self.state = PyvmpStates.INIT
        self.vmp_id = vmp_id
        self.health_event = Event()

    @staticmethod
    def peek(msg_id_msg_body: Dict[str, Dict]) -> Tuple[str, int]:
        """peek at first msg in msg_id_msg_body

        :param msg_id_msg_body:
        :type msg_id_msg_body: Dict[str, Dict]
        """
        msg_id = next(iter(msg_id_msg_body))
        return msg_id, msg_id_msg_body[msg_id][PyvmpProtocol.MSG_TYPE]

    @staticmethod
    def generate_msg_id():
        return str(shortuuid.uuid())

    def _check_connection(self, timeout) -> str:
        """check_connection with goweb
        If ack msg type is RESP_OK, set state to connected
        Else..Raise UnexpectedMessageException

        Raises: Timeout exception if no ack received in timeout. How to handle?
        """
        _logger.info("check connection")
        msg: Dict = self.adapter.receive(timeout)
        msg_id, msg_type = self.peek(msg)
        _logger.info("msg_type=%s, msg_id=%s", msg_type, msg_id)
        if msg_type == MessageType.SIG_OK.value:
            _logger.info("connection ok")
            self.state = PyvmpStates.CONNECTED
            return msg_id
        else:
            _logger.debug(
                "SIG_OK=%s, type=%s, msg_type_type=%s",
                MessageType.SIG_OK.value,
                type(MessageType.SIG_OK.value),
                type(msg_type),
            )
            raise UnexpectedMessageException(
                f"Unexpected message type, expecting={MessageType.SIG_OK.value}, received={msg_type}"
            )

    def health_reporter(self):
        _logger.info("health_reporter start")
        while True:
            if self.health_event.wait():
                self.adapter.send({GowebProtocolConst._PY_CODEC_SIGNAL_KEY: MessageConstants.HEARTBEAT})
                _logger.debug("heartbeat")
                time.sleep(PyvmpConstants.INTERVAL)
        _logger.debug("pyvmp|exit_heartbeat_reporter_thread")

    def _register(self, loaded: bool, msg: Dict, msg_id: str = ""):
        if not msg_id:
            _id = self.generate_msg_id()
        else:
            _id = msg_id
        if not loaded:
            _logger.debug("model not loaded")
            err_msg: Dict = msg
            self.state = PyvmpStates.MODEL_LOAD_FAILURE
            err_attr = {PyvmpProtocol.VMP_ID: self.vmp_id}
            reg_msg = construct_err_reg_msg(err_attr, err_msg)
        else:
            attr = msg
            attr[PyvmpProtocol.VMP_ID] = self.vmp_id
            self.state = PyvmpStates.MODEL_LOAD_SUCCESS
            reg_msg = construct_reg_msg(attr)
        # send registration message
        self.adapter.send({_id: reg_msg})

    def _load_models(self) -> Tuple[bool, Dict]:
        _logger.info("load models")
        try:
            model_verbs: List[str] = self.mc.load_model()
            model_attr: Dict = {PyvmpProtocol.API_VERBS: model_verbs}  # TODO: store model vmp attr here (eg verbs..etc)
            return True, model_attr
        except Exception as e:
            # return False, model_load
            _logger.exception("error loading models")
            error = model_loading_error.generate_error(details=repr(e))
            return (False, error[ek.ERROR])

    def _health_check(self):
        _logger.debug("waiting for health check...")
        msg = self.adapter.receive()
        msg_id, msg_type = self.peek(msg)
        _logger.info("msg_type=%s,msg_id=%s", msg_type, msg_id)
        if msg_type == MessageType.HEALTH_CHECK.value:
            health_check_response = {msg_id: MessageConstants.HEALTH_CHECK_OK}
            self.adapter.send(health_check_response)
        else:
            raise UnexpectedMessageException(
                f"Unexpected message type, expecting {MessageType.RESP_OK.value}, got={msg_type}"
            )

    def receive_msg(self) -> Tuple[str, int, Dict[str, Dict]]:
        msg: Dict[str, Dict]
        try:
            msg = self.adapter.receive(timeout=PyvmpConstants.INTERVAL)
        except Exception:  # TODO: Change to specific socket exception?
            self.health_event.set()
            msg = self.adapter.receive()
            self.health_event.clear()
        # NOTE: assume if first message type is REQ, all are of REQ type
        msg_id, msg_type = self.peek(msg)
        return msg_id, msg_type, msg

    def send_response(self, response):
        if len(response) > 0:
            self.adapter.send(response)
            _logger.info("pyvmp|send_response")

    def ask_for_work(self):
        _logger.info("vmpid=%s ask_for_work", self.vmp_id)
        self.adapter.send({GowebProtocolConst._PY_CODEC_SIGNAL_KEY: MessageConstants.ASK_FOR_WORK})

    def start(self):
        msg_id = self._check_connection(20)  # TODO: create timeout specific class for constants, for now just hard code
        loaded, msg = self._load_models()
        self._register(loaded, msg, msg_id)
        self._health_check()
        health_report_thread = Thread(name="health_report", daemon=True, target=self.health_reporter)
        health_report_thread.start()

        self.ask_for_work()
        _logger.info("starting event loop")
        while True:
            response: Dict = {}
            msg_id_msg_body: Dict[str, Dict]
            msg_id: str
            msg_type: str
            msg_id, msg_type, msg_id_msg_body = self.receive_msg()
            _logger.debug("received task from goweb")
            _logger.info("msg_id=%s,msg_type=%s", msg_id, msg_type)
            if msg_type == MessageType.REQ.value:
                # perform model prediction
                _logger.info("inference request")
                msg_type_req_output = self.mc.service_request(msg_id_msg_body)
                response = {**msg_type_req_output}
                _logger.debug("send response")
                self.send_response(response)

                self.ask_for_work()
            elif msg_type == MessageType.HEALTH_CHECK.value:
                _logger.info("health check")
                health_check_response = {msg_id: MessageConstants.HEALTH_CHECK_OK}
                response = {**health_check_response}
                self.send_response(response)
            elif msg_type == MessageType.EXIT.value:
                _logger.info("received exit msg")
                exit_status = {msg_id: MessageConstants.EXIT_OK}
                break
            else:
                _logger.warning("Unknown message type=%s", msg_type)
        return exit_status
