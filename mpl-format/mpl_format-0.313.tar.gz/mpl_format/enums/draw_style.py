from enum import Enum
from typing import Union

from mpl_format.enums.connection_style import CONNECTION_STYLE


class DRAW_STYLE(Enum):

    default = 0
    steps = 1
    steps_pre = 2
    steps_mid = 3
    steps_post = 4

    def get_name(self) -> str:

        return {
            'default': 'default',
            'steps': 'steps',
            'steps_pre': 'steps-pre',
            'steps_mid': 'steps-mid',
            'steps_post': 'steps-post'
        }[self.name]

    @staticmethod
    def get_draw_style(
            draw_style: Union[str, 'DRAW_STYLE']
    ) -> str:
        if draw_style and isinstance(draw_style, CONNECTION_STYLE):
            draw_style = draw_style.get_name()
        return draw_style
