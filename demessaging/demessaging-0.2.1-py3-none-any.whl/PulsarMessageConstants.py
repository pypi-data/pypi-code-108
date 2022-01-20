from enum import Enum


class PulsarConfigKeys(str, Enum):
    HOST = "host"
    PORT = "port"
    PERSISTENT = "persistent"
    TENANT = "tenant"
    NAMESPACE = "namespace"
    TOPIC = "topic"
    MAX_WORKERS = "max_workers"
    """(optional) number of concurrent workers for handling requests,
        default: number of processors on the machine, multiplied by 5"""
    QUEUE_SIZE = "queue_size"
    """(optional) size of the request queue,
        if MAX_WORKERS is set, this needs to be at least as big as MAX_WORKERS,
        otherwise an AttributeException is raised"""


class Status(str, Enum):

    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"


class PropertyKeys(str, Enum):
    REQUEST_CONTEXT = "requestContext"
    RESPONSE_TOPIC = "response_topic"
    REQUEST_MESSAGEID = "requestMessageId"
    MESSAGE_TYPE = "messageType"
    FRAGMENT = "fragment"
    NUM_FRAGMENTS = "num_fragments"
    STATUS = "status"


class MessageType(str, Enum):
    PING = "ping"
    PONG = "pong"
    REQUEST = "request"
    RESPONSE = "response"
    LOG = "log"
    INFO = "info"
    PROGRESS = "progress"
