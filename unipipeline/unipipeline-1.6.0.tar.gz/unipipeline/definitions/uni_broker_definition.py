from typing import Optional
from uuid import UUID

from unipipeline.definitions.uni_definition import UniDefinition
from unipipeline.definitions.uni_module_definition import UniModuleDefinition


class UniBrokerDefinition(UniDefinition):
    id: UUID
    type: UniModuleDefinition

    retry_max_count: int
    retry_delay_s: int

    external: Optional[str]

    content_type: str
    compression: Optional[str]

    @property
    def marked_as_external(self) -> bool:
        return self.external is not None
