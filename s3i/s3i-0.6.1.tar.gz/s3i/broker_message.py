import gzip
import json
import gnupg
import pgpy
from abc import ABC
from s3i.exception import raise_error_from_s3ib_msg, S3IBMessageError

GZIP_MAGIC_NUMBER = "1f8b"


class Message(ABC):
    def __init__(self, base_msg=None, gzip_msg=None, pgp_msg=None):
        if isinstance(base_msg, dict):
            raise_error_from_s3ib_msg(base_msg, S3IBMessageError)
            self.__base_msg = base_msg

        elif isinstance(base_msg, str):
            base_msg_json = json.loads(base_msg)
            raise_error_from_s3ib_msg(base_msg_json, S3IBMessageError)
            self.__base_msg = base_msg_json

        elif isinstance(base_msg, bytes):
            base_msg = str(base_msg, 'utf-8')
            base_msg_json = json.loads(base_msg)
            raise_error_from_s3ib_msg(base_msg_json, S3IBMessageError)
            self.__base_msg = base_msg_json

        else:
            self.__base_msg = {}

        if isinstance(pgp_msg, (str, bytes)):
            self.__pgp_msg = pgpy.pgp.PGPMessage.from_blob(pgp_msg)
        elif isinstance(pgp_msg, pgpy.pgp.PGPMessage):
            self.__pgp_msg = pgp_msg
        else:
            self.__pgp_msg = pgpy.PGPMessage.new("")

        if isinstance(gzip_msg, bytes):
            if gzip_msg.hex()[0:4] == GZIP_MAGIC_NUMBER:
                self.__gzip_msg = gzip_msg
            else:
                raise ValueError("Invalid gzip header")
        else:
            self.__gzip_msg = b''

    @property
    def base_msg(self):
        return self.__base_msg

    @base_msg.setter
    def base_msg(self, value):
        if isinstance(value, dict):
            raise_error_from_s3ib_msg(value, S3IBMessageError)
            self.__base_msg = value
        else:
            raise TypeError("Only dict typed message is valid")

    @property
    def pgp_msg(self):
        return self.__pgp_msg

    @pgp_msg.setter
    def pgp_msg(self, value):
        if isinstance(value, pgpy.pgp.PGPMessage):
            self.__pgp_msg = value
        else:
            raise TypeError("Only message typed with pgpy.pgp.PGPMessage is valid")

    @property
    def gzip_msg(self):
        return self.__gzip_msg

    @gzip_msg.setter
    def gzip_msg(self, value):
        if isinstance(value, bytes):
            if value.hex()[0:4] == GZIP_MAGIC_NUMBER:
                self.__gzip_msg = value
            else:
                raise ValueError("Invalid gzip header")
        else:
            raise TypeError("Only bytes typed message is valid")

    def convert_base_to_pgp(self):
        self.pgp_msg = pgpy.PGPMessage.new(json.dumps(self.__base_msg))
        return self.pgp_msg

    def convert_pgp_to_base(self):
        if self.pgp_msg.is_encrypted:
            raise ValueError("PGP Message is still encrypted")
        else:
            self.base_msg = json.loads(self.__pgp_msg.message)
            return self.base_msg

    def convert_gzip_to_pgp(self):
        self.pgp_msg = pgpy.PGPMessage.new(self.__gzip_msg)
        return self.pgp_msg

    def convert_pgp_to_gzip(self):
        if self.pgp_msg.is_encrypted:
            raise ValueError("PGP Message is still encrypted")
        else:
            if not isinstance(self.pgp_msg.message, bytearray):
                raise ValueError("PGP Message can not be converted to GZIP data")
            self.gzip_msg = bytes(self.pgp_msg.message)
            return self.gzip_msg

    def sign(self, sec_key, msg_pgp):
        if not isinstance(sec_key, type(pgpy.PGPKey())):
            raise TypeError("Invalid type of secret key")
        if not isinstance(msg_pgp, pgpy.pgp.PGPMessage):
            raise TypeError("Only PGP Message is valid")
        msg_pgp |= sec_key.sign(msg_pgp)
        self.pgp_msg = msg_pgp
        return self.pgp_msg

    @staticmethod
    def verify(pub_key, msg_pgp):
        if not isinstance(pub_key, type(pgpy.PGPKey())):
            raise TypeError("Invalid type of public key")
        if not isinstance(msg_pgp, pgpy.pgp.PGPMessage):
            raise TypeError("Only PGP Message is valid")
        try:
            pub_key.verify(msg_pgp)
            return True
        except pgpy.errors.PGPError:
            return False

    def encrypt(self, pub_key, msg_pgp):
        if not isinstance(pub_key, type(pgpy.PGPKey())):
            raise TypeError("Invalid type of public key")
        if not isinstance(msg_pgp, pgpy.pgp.PGPMessage):
            raise TypeError("Only PGP Message is valid")
        cipher = pgpy.constants.SymmetricKeyAlgorithm.AES256
        session_key = cipher.gen_key()
        self.pgp_msg = pub_key.encrypt(msg_pgp, cipher=cipher, sessionkey=session_key) # TODO: double print of logs
        return self.pgp_msg

    def decrypt(self, sec_key, msg_pgp):
        if not isinstance(sec_key, type(pgpy.PGPKey())):
            raise TypeError("Invalid type of public key")
        if not isinstance(msg_pgp, pgpy.pgp.PGPMessage):
            raise TypeError("Only PGP Message is valid")
        self.pgp_msg = sec_key.decrypt(msg_pgp)
        return self.pgp_msg

    def compress(self, msg_json, level):
        if not isinstance(level, int):
            raise TypeError("Unexpected type for the input level")
        self.gzip_msg = gzip.compress(bytes(json.dumps(msg_json), 'utf-8'), compresslevel=level)
        return self.gzip_msg

    def decompress(self, msg_gzip):
        if not isinstance(msg_gzip, bytes):
            raise TypeError("Unexpected type")
        if msg_gzip.hex()[0:4] != GZIP_MAGIC_NUMBER:
            raise TypeError("Unexpected gzip header")
        self.base_msg = json.loads(gzip.decompress(msg_gzip))
        return self.base_msg


class UserMessage(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillUserMessage(self,
                        sender,
                        receivers,
                        subject,
                        text,
                        message_id,
                        reply_to_endpoint=None,
                        replying_to_msg=None,
                        attachments=None
                        ):

        _user_message_json = {
            "sender": sender,
            "identifier": message_id,
            "receivers": receivers,
            "messageType": "userMessage",
            "subject": subject,
            "text": text
        }
        if replying_to_msg is not None:
            _user_message_json["replyingToMessage"] = replying_to_msg
        if reply_to_endpoint is not None:
            _user_message_json["replyToEndpoint"] = reply_to_endpoint
        if isinstance(attachments, list):
            _user_message_json["attachments"] = [
                {"filename": "", "data": ""} for att in attachments
            ]
            for i in range(len(attachments)):
                _user_message_json["attachments"][i]["filename"] = attachments[i]["filename"]
                _user_message_json["attachments"][i]["data"] = attachments[i]["data"]

        self.base_msg = _user_message_json


class ServiceRequest(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillServiceRequest(self,
                           sender,
                           receivers,
                           message_id,
                           service_type,
                           parameters=None,
                           reply_to_endpoint=None,
                           replying_to_msg=None,
                           ):
        _service_req_json = {
            "sender": sender,
            "identifier": message_id,
            "receivers": receivers,
            "messageType": "serviceRequest",
            "serviceType": service_type,
        }
        if replying_to_msg is not None:
            _service_req_json["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _service_req_json["replyToEndpoint"] = reply_to_endpoint

        if parameters is not None:
            _service_req_json["parameters"] = parameters

        self.base_msg = _service_req_json


class ServiceReply(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillServiceReply(self,
                         sender,
                         receivers,
                         message_id,
                         service_type,
                         results=None,
                         reply_to_endpoint=None,
                         replying_to_msg=None,
                        ):
        _service_reply_json = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "messageType": "serviceReply",
            "serviceType": service_type
        }

        if replying_to_msg is not None:
            _service_reply_json["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _service_reply_json["replyToEndpoint"] = reply_to_endpoint

        if results is not None:
            _service_reply_json["results"] = results

        self.base_msg = _service_reply_json


class GetValueRequest(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillGetValueRequest(self,
                            sender,
                            receivers,
                            message_id,
                            attribute_path,
                            reply_to_endpoint=None,
                            replying_to_msg=None,
                            ):

        _get_value_req = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "attributePath":attribute_path,
            "messageType": "getValueRequest"
        }

        if replying_to_msg is not None:
            _get_value_req["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _get_value_req["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _get_value_req


class GetValueReply(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillGetValueReply(self,
                          sender,
                          receivers,
                          message_id,
                          value,
                          reply_to_endpoint=None,
                          replying_to_msg=None,
                          ):
        _get_value_reply = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "value": value,
            "messageType": "getValueReply"
        }
        if replying_to_msg is not None:
            _get_value_reply["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _get_value_reply["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _get_value_reply


class SetValueRequest(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillSetValueRequest(self,
                            sender,
                            receivers,
                            message_id,
                            attribute_path,
                            new_value,
                            reply_to_endpoint=None,
                            replying_to_msg=None,
                            ):

        _set_value_req = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "attributePath": attribute_path,
            "newValue": new_value,
            "messageType":"setValueRequest"
        }

        if replying_to_msg is not None:
            _set_value_req["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _set_value_req["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _set_value_req


class SetValueReply(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillSetValueReply(self,
                          sender,
                          receivers,
                          message_id,
                          ok,
                          reply_to_endpoint=None,
                          replying_to_msg=None,
                          ):
        _set_value_reply = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "ok": ok,
            "messageType": "setValueReply"
        }

        if replying_to_msg is not None:
            _set_value_reply["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _set_value_reply["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _set_value_reply


class CustomEventRequest(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillCustomEventRequest(self,
                               sender,
                               receivers,
                               message_id,
                               filter,
                               attribute_paths,
                               reply_to_endpoint=None,
                               replying_to_msg=None,
                               ):

        _custom_event_req = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "filter": filter,
            "attributePaths": attribute_paths,
            "messageType": "customEventRequest"
        }
        if replying_to_msg is not None:
            _custom_event_req["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _custom_event_req["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _custom_event_req


class CustomEventReply(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillCustomEventReply(self,
                             sender,
                             receivers,
                             message_id,
                             topic,
                             status,
                             reply_to_endpoint=None,
                             replying_to_msg=None,
                             ):
        _custom_event_reply = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "topic": topic,
            "status": status,
            "messageType": "customEventReply"
        }

        if replying_to_msg is not None:
            _custom_event_reply["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _custom_event_reply["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _custom_event_reply


class EventMessage(Message):
    def __init__(self, base_msg=None, pgp_msg=None, gzip_msg=None):
        super().__init__(
            base_msg=base_msg,
            pgp_msg=pgp_msg,
            gzip_msg=gzip_msg
        )

    def fillEventMessage(self,
                         sender,
                         receivers,
                         message_id,
                         topic,
                         timestamp,
                         content,
                         reply_to_endpoint=None,
                         replying_to_msg=None,
                         ):

        _event_message = {
            "sender": sender,
            "receivers": receivers,
            "identifier": message_id,
            "topic": topic,
            "timestamp": timestamp,
            "content": content,
            "messageType": "eventMessage"
        }

        if replying_to_msg is not None:
            _event_message["replyingToMessage"] = replying_to_msg

        if reply_to_endpoint is not None:
            _event_message["replyToEndpoint"] = reply_to_endpoint

        self.base_msg = _event_message