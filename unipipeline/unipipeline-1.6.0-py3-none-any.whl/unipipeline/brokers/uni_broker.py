from typing import Set, List, TYPE_CHECKING, Generic, TypeVar, Type, Optional, Dict, Any

from pydantic import ValidationError
from atexit import register as on_exit_app

from unipipeline.brokers.uni_broker_consumer import UniBrokerConsumer
from unipipeline.definitions.uni_broker_definition import UniBrokerDefinition
from unipipeline.definitions.uni_definition import UniDynamicDefinition
from unipipeline.utils.uni_echo import UniEcho
from unipipeline.message_meta.uni_message_meta import UniMessageMeta, UniAnswerParams

if TYPE_CHECKING:
    from unipipeline.modules.uni_mediator import UniMediator


TConf = TypeVar('TConf')


class UniBroker(Generic[TConf]):
    config_type: Type[TConf] = UniDynamicDefinition  # type: ignore

    def __init__(self, mediator: 'UniMediator', definition: UniBrokerDefinition) -> None:
        self._uni_definition = definition
        self._uni_mediator = mediator
        self._uni_echo = self._uni_mediator.echo.mk_child(f'broker[{self._uni_definition.name}]')

        try:
            self._uni_conf = self._uni_definition.configure_dynamic(self.config_type)  # type: ignore
        except ValidationError as e:
            self._uni_echo.exit_with_error(str(e))

        on_exit_app(self.close)

    @property
    def config(self) -> TConf:
        return self._uni_conf

    def serialize_message_body(self, meta: UniMessageMeta) -> bytes:
        data_dict: Dict[str, Any] = meta.payload if meta.unwrapped else meta.dict()
        data_bytes = self._uni_mediator.serialize_content_type(self.definition.content_type, data_dict)
        data_bytes = self._uni_mediator.compress_message_body(self.definition.compression, data_bytes)
        return data_bytes

    def parse_message_body(self, content: bytes, compression: Optional[str], content_type: str, unwrapped: bool) -> UniMessageMeta:
        content = self._uni_mediator.decompress_message_body(compression, content)
        fields = self._uni_mediator.parse_content_type(content_type, content)
        if unwrapped:
            return UniMessageMeta.create_new(fields, unwrapped=True)
        return UniMessageMeta(**fields)

    def connect(self) -> None:
        raise NotImplementedError(f'method connect must be implemented for {type(self).__name__}')

    def close(self) -> None:
        raise NotImplementedError(f'method close must be implemented for {type(self).__name__}')

    def add_consumer(self, consumer: UniBrokerConsumer) -> None:
        raise NotImplementedError(f'method consume must be implemented for {type(self).__name__}')

    def stop_consuming(self) -> None:
        raise NotImplementedError(f'method stop_consuming must be implemented for {type(self).__name__}')

    def start_consuming(self) -> None:
        raise NotImplementedError(f'method start_consuming must be implemented for {type(self).__name__}')

    def publish(self, topic: str, meta_list: List[UniMessageMeta], alone: bool = False) -> None:
        raise NotImplementedError(f'method publish must be implemented for {type(self).__name__}')

    def rpc_call(self, topic: str, meta: UniMessageMeta, *, alone: bool = False, max_delay_s: int = 1, unwrapped: bool = False) -> Optional[UniMessageMeta]:
        raise NotImplementedError(f'method rpc_call must be implemented for {type(self).__name__}')

    def get_topic_approximate_messages_count(self, topic: str) -> int:
        raise NotImplementedError(f'method get_topic_size must be implemented for {type(self).__name__}')

    def initialize(self, topics: Set[str], answer_topics: Set[str]) -> None:
        raise NotImplementedError(f'method initialize must be implemented for {type(self).__name__}')

    def publish_answer(self, answer_params: UniAnswerParams, meta: UniMessageMeta) -> None:
        raise NotImplementedError(f'method publish_answer must be implemented for {type(self).__name__}')

    @property
    def definition(self) -> UniBrokerDefinition:
        return self._uni_definition

    @property
    def echo(self) -> UniEcho:
        return self._uni_echo
