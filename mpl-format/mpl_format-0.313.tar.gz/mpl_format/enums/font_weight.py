from enum import Enum
from typing import Union


class FONT_WEIGHT(Enum):

    ultra_light = 0
    light = 1
    normal = 2
    regular = 3
    book = 4
    medium = 5
    roman = 6
    semi_bold = 7
    demi_bold = 8
    demi = 9
    bold = 10
    heavy = 11
    extra_bold = 12
    black = 13

    def get_name(self) -> str:

        return {
            'ultra_light': 'ultralight',
            'light': 'light',
            'normal': 'normal',
            'regular': 'regular',
            'book': 'book',
            'medium': 'medium',
            'roman': 'roman',
            'semi_bold': 'semibold',
            'demi_bold': 'demibold',
            'demi': 'demi',
            'bold': 'bold',
            'heavy': 'heavy',
            'extra_bold': 'extra bold',
            'black': 'black'
        }[self.name]

    @staticmethod
    def get_font_weight(
            font_weight: Union[int, float, 'FONT_WEIGHT']
    ) -> Union[str, int, float]:
        if font_weight and isinstance(font_weight, FONT_WEIGHT):
            font_weight = font_weight.get_name()
        return font_weight
