from enum import Enum
from typing import Union


class FONT_SIZE(Enum):

    xx_small = 0
    x_small = 1
    small = 2
    medium = 3
    large = 4
    x_large = 5
    xx_large = 6

    def get_name(self) -> str:

        return {
            'xx_small': 'xx-small',
            'x_small': 'x-small',
            'small': 'small',
            'medium': 'medium',
            'large': 'large',
            'x_large': 'x-large',
            'xx_large': 'xx-large'
        }[self.name]

    @staticmethod
    def get_font_size(
            font_size: Union[int, float, 'FONT_SIZE']
    ) -> Union[str, int, float]:
        if font_size and isinstance(font_size, FONT_SIZE):
            font_size = font_size.get_name()
        return font_size
