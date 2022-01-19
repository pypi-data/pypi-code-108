from typing import Union

from mpl_format.animation.kwarg_animations.color_animation import ColorAnimation
from mpl_format.animation.kwarg_animations.float_animation import FloatAnimation
from mpl_format.compound_types import Color

FloatOrFloatAnimation = Union[float, FloatAnimation]
StrOrFloatAnimation = Union[str, FloatAnimation]
StrOrFloatOrFloatAnimation = Union[str, float, FloatAnimation]
ColorOrColorAnimation = Union[Color, ColorAnimation]
