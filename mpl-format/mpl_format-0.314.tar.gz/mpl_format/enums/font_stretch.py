from enum import Enum
from typing import Union


class FONT_STRETCH(Enum):

    ultra_condensed = 0
    extra_condensed = 1
    condensed = 2
    semi_condensed = 3
    normal = 4
    semi_expanded = 5
    expanded = 6
    extra_expanded = 7
    ultra_expanded = 8

    def get_name(self) -> str:

        return {
            'ultra_condensed': 'ultra-condensed',
            'extra_condensed': 'extra-condensed',
            'condensed': 'condensed',
            'semi_condensed': 'semi-condensed',
            'normal': 'normal',
            'semi_expanded': 'semi-expanded',
            'expanded': 'expanded',
            'extra_expanded': 'extra-expanded',
            'ultra_expanded': 'ultra-expanded'
        }[self.name]

    @staticmethod
    def get_font_stretch(
            font_stretch: Union[int, float, 'FONT_STRETCH']
    ) -> Union[str, int, float]:
        if font_stretch and isinstance(font_stretch, FONT_STRETCH):
            font_stretch = font_stretch.get_name()
        return font_stretch
