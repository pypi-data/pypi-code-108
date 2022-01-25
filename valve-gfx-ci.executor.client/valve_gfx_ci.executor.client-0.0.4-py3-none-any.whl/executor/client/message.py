# WARNING: Changes to this file need to be backwards/forwards compatible
# WARNING 2: You will need to edit the client's message.py file yourself!

from dataclasses import dataclass, field
from functools import cached_property
from collections import namedtuple
from datetime import datetime
from enum import Enum, IntEnum

import struct
import base64
import json


class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class JobStatus(Enum):
    PASS = 0
    WARN = 1
    COMPLETE = 2
    FAIL = 3
    INCOMPLETE = 4
    UNKNOWN = 5
    SETUP_FAIL = 6

    @classmethod
    def from_str(cls, status):
        return getattr(cls, status, cls.UNKNOWN)

    @property
    def status_code(self):
        return self.value


class MessageType(Enum):
    CONTROL = "ctrl"  # A message meant to explain what is going on either ends
    JOB_IO = "job_io"
    SESSION_END = "session_end"

    @property
    def message_class(self):
        if self == self.CONTROL:
            return ControlMessage
        elif self == self.JOB_IO:
            return JobIOMessage
        elif self == self.SESSION_END:
            return SessionEndMessage


@dataclass
class Message:
    payload: str
    date: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def recv(cls, sock, length):
        buf = bytearray(length)
        view = memoryview(buf)

        cur = 0
        while cur < length:
            received = sock.recv_into(view, length - cur)
            if received == 0:
                raise EOFError("The connection got interrupted before receiving the end of the message")

            cur += received
            view = view[cur:]

        return buf

    @classmethod
    def next_message(self, sock):
        length = struct.unpack("!I", self.recv(sock, 4))[0]
        frame = self.recv(sock, length)

        msg = json.loads(frame.decode())
        MessageTypeClass = MessageType(msg.get("msg_type")).message_class

        return MessageTypeClass(msg.get("payload"),
                                date=datetime.fromisoformat(msg.get('date')))

    def send(self, sock):
        payload = json.dumps({
            "msg_type": self.msg_type.value,
            "date": self.date.isoformat(),
            "payload": self.payload
        }).encode()

        return sock.send(struct.pack("!I", len(payload)) + payload)


class ControlMessage(Message):
    msg_type = MessageType.CONTROL

    @property
    def message(self):
        return self.payload.get("msg")

    @property
    def severity(self):
        return self.payload.get("severity")

    @classmethod
    def create(cls, message, severity=LogLevel.INFO):
        return cls(payload={
            "msg": message,
            "severity": severity
        })


class JobIOMessage(Message):
    msg_type = MessageType.JOB_IO

    @property
    def buffer(self):
        return base64.b85decode(self.payload.encode())

    @classmethod
    def create(cls, buffer):
        return cls(payload=base64.b85encode(buffer).decode())


class SessionEndMessage(Message):
    msg_type = MessageType.SESSION_END

    @property
    def status(self):
        return JobStatus.from_str(self.payload.get("status"))

    @cached_property
    def job_bucket(self):
        bucket = self.payload.get("job_bucket")
        if bucket is None:
            return None

        JobBucket = namedtuple("JobBucket", ["minio_access_url", "bucket_name"])
        return JobBucket(minio_access_url=bucket.get('minio_access_url'),
                         bucket_name=bucket.get('bucket_name'))

    @classmethod
    def create(cls, status, job_bucket=None):
        parameters = {
            "status": status.name
        }

        if job_bucket:
            # TODO: Grant only read rights to the client
            job_bucket.create_owner_credentials("client")
            parameters['job_bucket'] = {
                "minio_access_url": job_bucket.access_url("client"),
                "bucket_name": job_bucket.name
            }

        return cls(payload=parameters)
