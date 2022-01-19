from enum import Enum
from typing import Optional, Union


class CAP_STYLE(Enum):

    butt = 1
    round = 2
    projecting = 3

    @staticmethod
    def get_cap_style(
            cap_style: Optional[Union[str, 'CAP_STYLE']] = None
    ) -> str:
        if cap_style and isinstance(cap_style, CAP_STYLE):
            cap_style = cap_style.name
        return cap_style
