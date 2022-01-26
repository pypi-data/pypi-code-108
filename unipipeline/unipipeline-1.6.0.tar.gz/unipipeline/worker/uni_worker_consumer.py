from typing import TypeVar, Generic, Optional, Type, Any, Union, Dict, TYPE_CHECKING

from unipipeline.errors.uni_payload_error import UniPayloadParsingError, UniAnswerPayloadParsingError
from unipipeline.errors.uni_sending_to_worker_error import UniSendingToWorkerError
from unipipeline.answer.uni_answer_message import UniAnswerMessage
from unipipeline.brokers.uni_broker_message_manager import UniBrokerMessageManager
from unipipeline.errors.uni_work_flow_error import UniWorkFlowError
from unipipeline.message.uni_message import UniMessage
from unipipeline.message_meta.uni_message_meta import UniMessageMeta, UniMessageMetaErrTopic, UniAnswerParams
from unipipeline.worker.uni_worker import UniWorker
from unipipeline.worker.uni_worker_consumer_manager import UniWorkerConsumerManager
from unipipeline.worker.uni_worker_consumer_message import UniWorkerConsumerMessage
from unipipeline.definitions.uni_worker_definition import UniWorkerDefinition

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator

TInputMsgPayload = TypeVar('TInputMsgPayload', bound=UniMessage)
TAnswerMsgPayload = TypeVar('TAnswerMsgPayload', bound=Optional[UniMessage])


class UniWorkerConsumer(Generic[TInputMsgPayload, TAnswerMsgPayload]):
    def __init__(self, definition: UniWorkerDefinition, mediator: 'UniMediator', worker_type: Type[UniWorker[TInputMsgPayload, TAnswerMsgPayload]]) -> None:
        self._definition = definition
        self._mediator = mediator

        self._worker_manager = UniWorkerConsumerManager(self.send_to)
        self._worker = worker_type(self._worker_manager)
        self._uni_echo = mediator.echo.mk_child(f'worker[{definition.name}]')

        self._input_message_type: Type[TInputMsgPayload] = mediator.get_message_type(self._definition.input_message.name)  # type: ignore
        self._answer_message_type: Optional[Type[TAnswerMsgPayload]] = mediator.get_message_type(self._definition.answer_message.name) if self._definition.answer_message is not None else None  # type: ignore

        self._current_meta: Optional[UniMessageMeta] = None

    def send_to(self, worker: Union[Type['UniWorker[Any, Any]'], str], data: Union[Dict[str, Any], UniMessage], *, alone: bool = False, need_answer: bool = False) -> Optional[UniAnswerMessage[UniMessage]]:
        wd = self._mediator.config.get_worker_definition(worker)
        if wd.name not in self._definition.output_workers:
            raise UniSendingToWorkerError(f'worker {wd.name} is not defined in workers->{self._definition.name}->output_workers')
        if need_answer and not wd.need_answer:
            raise UniWorkFlowError(f'you will get no response form worker {wd.name}')
        if need_answer:
            answ_params = UniAnswerParams(topic=self._definition.answer_topic, id=self._worker_manager.id)
            return self._mediator.send_to(wd.name, data, parent_meta=self._current_meta, answer_params=answ_params, alone=alone)
        self._mediator.send_to(wd.name, data, parent_meta=self._current_meta, answer_params=None, alone=alone)
        return None

    def process_message(self, meta: UniMessageMeta, manager: UniBrokerMessageManager) -> None:
        self._current_meta = meta
        msg = UniWorkerConsumerMessage[TInputMsgPayload](self._input_message_type, manager, meta)

        try:
            result: Optional[Union[TAnswerMsgPayload, Dict[str, Any]]] = self._worker.handle_message(msg)
        except UniAnswerPayloadParsingError as e:
            self._mediator.move_to_error_topic(self._definition, meta, UniMessageMetaErrTopic.HANDLE_MESSAGE_ERR, e)
        except UniPayloadParsingError as e:
            self._mediator.move_to_error_topic(self._definition, meta, UniMessageMetaErrTopic.MESSAGE_PAYLOAD_ERR, e)
        # except Exception as e:  # TODO: correct error handling
        #     self._mediator.move_to_error_topic(self._definition, meta, UniMessageMetaErrTopic.HANDLE_MESSAGE_ERR, e)
        else:
            if self._definition.need_answer:
                try:
                    self._mediator.answer_to(self._definition.name, meta, result, unwrapped=self._definition.answer_unwrapped)
                except UniSendingToWorkerError:
                    pass

        if self._definition.ack_after_success:
            msg.ack()
        self._current_meta = None
