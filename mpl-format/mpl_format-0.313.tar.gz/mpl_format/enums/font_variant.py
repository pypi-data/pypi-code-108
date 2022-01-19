from enum import Enum
from typing import Union


class FONT_VARIANT(Enum):

    normal = 0
    small_caps = 1

    def get_name(self) -> str:

        return {
            'normal': 'normal',
            'small_caps': 'small-caps'
        }[self.name]

    @staticmethod
    def get_font_variant(
            font_variant: Union[str, 'FONT_VARIANT']
    ) -> Union[str, int, float]:
        if font_variant and isinstance(font_variant, FONT_VARIANT):
            font_variant = font_variant.get_name()
        return font_variant
