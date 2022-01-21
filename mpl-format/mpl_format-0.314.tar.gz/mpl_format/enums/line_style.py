from enum import Enum
from typing import Optional, Union


class LINE_STYLE(Enum):

    solid = 1
    dashed = 2
    dash_dot = 3
    dotted = 4

    def get_name(self) -> str:

        return {
            'solid': 'solid',
            'dashed': 'dashed',
            'dash_dot': 'dashdot',
            'dotted': 'dotted',
        }[self.name]

    @staticmethod
    def get_line_style(
            line_style: Optional[Union[str, 'LINE_STYLE']] = None) -> str:
        if line_style and isinstance(line_style, LINE_STYLE):
            line_style = line_style.name
        return line_style
