from enum import Enum
from typing import Union

from matplotlib.patches import BoxStyle


class BOX_STYLE(Enum):

    circle = 0
    double_arrow = 1
    left_arrow = 2
    right_arrow = 3
    round = 4
    round_4 = 5
    round_tooth = 6
    saw_tooth = 7
    square = 8

    def get_name(self) -> str:

        return {
            'circle': 'circle',
            'double_arrow': 'darrow',
            'left_arrow': 'larrow',
            'right_arrow': 'rarrow',
            'round': 'round',
            'round_4': 'round4',
            'round_tooth': 'roundtooth',
            'saw_tooth': 'sawtooth',
            'square': 'square'
        }[self.name]

    @staticmethod
    def get_box_style(
            box_style: Union[str, 'BOX_STYLE']
    ) -> str:
        if box_style and isinstance(box_style, BOX_STYLE):
            box_style = box_style.get_name()
        return box_style


BoxStyleType = Union[
    str, BOX_STYLE,
    BoxStyle.Circle, BoxStyle.Round, BoxStyle.Round4,
    BoxStyle.DArrow, BoxStyle.LArrow, BoxStyle.RArrow,
    BoxStyle.Roundtooth, BoxStyle.Sawtooth, BoxStyle.Square
]
