from enum import Enum
from typing import Optional, Union


class JOIN_STYLE(Enum):

    miter = 1
    round = 2
    bevel = 3

    @staticmethod
    def get_join_style(
            join_style: Optional[Union[str, 'JOIN_STYLE']] = None
    ) -> str:
        if join_style and isinstance(join_style, JOIN_STYLE):
            join_style = join_style.name
        return join_style
