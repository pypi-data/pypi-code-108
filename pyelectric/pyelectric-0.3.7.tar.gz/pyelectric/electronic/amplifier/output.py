from abc import ABC, abstractstaticmethod
from typing import List


class Output(ABC):
    @abstractstaticmethod
    def get_parameter_names() -> List[str]:
        return ['Zi', 'Zo', 'Avnl']
