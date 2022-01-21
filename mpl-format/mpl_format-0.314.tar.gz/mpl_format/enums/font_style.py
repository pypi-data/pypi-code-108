from enum import Enum
from typing import Union


class FONT_STYLE(Enum):

    normal = 0
    italic = 1
    oblique = 2

    @staticmethod
    def get_font_style(
            font_style: Union[int, float, 'FONT_STYLE']
    ) -> Union[str, int, float]:
        if font_style and isinstance(font_style, FONT_STYLE):
            font_style = font_style.get_name()
        return font_style
