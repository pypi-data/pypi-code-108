import dataclasses
from typing import Dict, Optional, ClassVar

from pika.exchange_type import ExchangeType

from . import constants


@dataclasses.dataclass(frozen=True, eq=False)
class Queue:
    name: str
    declare: bool = True
    durable: bool = True
    auto_delete: bool = False
    exclusive: bool = False
    arguments: Optional[Dict[str, str]] = None

    GENERATED: ClassVar[str] = ''

    def __eq__(self, other):
        if isinstance(other, Queue):
            return self.name == other.name
        else:
            return NotImplemented


@dataclasses.dataclass(frozen=True, eq=False)
class Exchange:
    name: str
    declare: bool = True
    type: str = ExchangeType.direct.value
    durable: bool = True
    auto_delete: bool = False
    arguments: Optional[Dict[str, str]] = None

    def __eq__(self, other):
        if isinstance(other, Exchange):
            return self.name == other.name
        else:
            return NotImplemented


DEFAULT_EXCHANGE: Exchange = Exchange(name=constants.DEFAULT_EXCHANGE_NAME,
                                      type=ExchangeType.direct.value,
                                      durable=True,
                                      declare=False)

DEAD_LETTER_EXCHANGE: Exchange = Exchange(name=constants.DEAD_LETTER_EXCHANGE_NAME,
                                          type=constants.DEAD_LETTER_EXCHANGE_TYPE.value,
                                          durable=True,
                                          declare=False)

DEAD_LETTER_QUEUE: Queue = Queue(name=constants.DEAD_LETTER_QUEUE_NAME,
                                 durable=True,
                                 declare=False)

TRANSCRIPTION_RESULT_WAITING_EXCHANGE: Exchange = Exchange(name=constants.TRANSCRIPTION_RESULT_WAITING_EXCHANGE_NAME,
                                                           durable=True,
                                                           declare=False,
                                                           type=ExchangeType.fanout.value)
