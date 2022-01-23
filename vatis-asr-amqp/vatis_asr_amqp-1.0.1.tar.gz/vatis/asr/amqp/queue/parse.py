import cgi
from typing import Union, Tuple

import jsonpickle

from . import environment
from .consumer import Message
from .exceptions import UnknownBodyTypeException, CorruptedBodyException
from vatis.asr_commons.config.logging import get_logger

logger = get_logger(__name__)


def decode(message: Message) -> Union[object, str, bytes]:
    try:
        content_type, options = cgi.parse_header(message.headers.get('Content-Type', ''))
    except Exception as e:
        logger.exception('Can\'t decode content type: %s', str(e))
        raise UnknownBodyTypeException()

    try:
        if content_type == 'application/json':
            decoded_body: str = str(message.body, options.get('charset', environment.CHARSET))
            return jsonpickle.decode(decoded_body)
        elif content_type == 'text/plain':
            return str(message.body, options.get('charset', environment.CHARSET))
        elif content_type == 'application/octet-stream':
            return message.body
        else:
            raise UnknownBodyTypeException(content_type)
    except Exception as e:
        logger.exception('Can\'t decode body: %s', str(e))
        raise CorruptedBodyException()


def encode(payload: Union[object, str, bytes]) -> Tuple[bytes, str]:
    try:
        if isinstance(payload, str):
            body: bytes = payload.encode(encoding=environment.CHARSET)
            return body, f'text/plain; charset={environment.CHARSET}'
        elif isinstance(payload, bytes):
            return payload, 'application/octet-stream'
        else:
            json_payload: str = jsonpickle.encode(payload)
            body: bytes = json_payload.encode(encoding=environment.CHARSET)
            return body, f'application/json; charset={environment.CHARSET}'
    except Exception as e:
        raise CorruptedBodyException()
