from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
import uuid

# Prevent circular dependency
if TYPE_CHECKING:
    from jetpack._task.jetpack_function_with_client import JetpackFunctionWithClient


class Task:
    def __init__(
        self,
        jetpack_function: JetpackFunctionWithClient[Any],
        target_time: int,
        is_scheduled: bool,
    ):
        self.jetpack_function = jetpack_function
        self.target_time = target_time
        self.id: Optional[uuid.UUID] = None
        self.is_scheduled = is_scheduled

    def symbol_name(self) -> str:
        return self.jetpack_function.name()
