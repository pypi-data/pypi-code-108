from typing import Any
from copy import deepcopy


class Methods:
    @staticmethod
    def try_copy(item: Any) -> Any:
        """
        A failsafe deepcopy wrapper
        """

        try:
            return deepcopy(item)

        except:
            return item
