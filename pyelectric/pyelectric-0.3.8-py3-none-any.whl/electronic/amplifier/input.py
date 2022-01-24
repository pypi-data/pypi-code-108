from abc import ABC, abstractstaticmethod
from typing import List


class Input(ABC):
    @abstractstaticmethod
    def get_parameter_names() -> List[str]:
        pass
