from typing import Set, Optional
from uuid import UUID

from unipipeline.definitions.uni_broker_definition import UniBrokerDefinition
from unipipeline.definitions.uni_definition import UniDefinition
from unipipeline.definitions.uni_message_definition import UniMessageDefinition
from unipipeline.definitions.uni_module_definition import UniModuleDefinition
from unipipeline.definitions.uni_waiting_definition import UniWaitingDefinition


class UniWorkerDefinition(UniDefinition):
    id: UUID
    name: str
    broker: UniBrokerDefinition
    type: Optional[UniModuleDefinition]
    topic: str
    prefetch_count: int
    error_topic: str
    error_payload_topic: str
    answer_topic: str
    input_message: UniMessageDefinition
    answer_message: Optional[UniMessageDefinition]
    output_workers: Set[str]
    ack_after_success: bool
    waitings: Set[UniWaitingDefinition]
    external: Optional[str]
    input_unwrapped: bool
    answer_unwrapped: bool
    answer_avg_delay_s: int

    @property
    def marked_as_external(self) -> bool:
        return self.external is not None

    @property
    def need_answer(self) -> bool:
        return self.answer_message is not None
