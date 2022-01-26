from typing import Generic, Any, TypeVar, Optional, Dict, Union

from unipipeline.message.uni_message import UniMessage
from unipipeline.worker.uni_worker_consumer_manager import UniWorkerConsumerManager
from unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage

TInputMessage = TypeVar('TInputMessage', bound=UniMessage)
TOutputMessage = TypeVar('TOutputMessage', bound=Optional[UniMessage])


class UniWorker(Generic[TInputMessage, TOutputMessage]):
    def __init__(self, manager: UniWorkerConsumerManager) -> None:
        self._uni_manager = manager

    @property
    def manager(self) -> UniWorkerConsumerManager:
        return self._uni_manager

    def handle_message(self, msg: UniWorkerConsumerMessage[TInputMessage]) -> Optional[Union[TOutputMessage, Dict[str, Any]]]:
        raise NotImplementedError(f'method handle_message not implemented for {type(self).__name__}')
