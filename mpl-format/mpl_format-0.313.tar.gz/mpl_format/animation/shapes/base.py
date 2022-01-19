from typing import Optional

from mpl_format.animation.kwarg_animations.color_animation import ColorAnimation
from mpl_format.animation.kwarg_animations.float_animation import FloatAnimation
from mpl_format.animation.type_animations import StrOrFloatAnimation
from mpl_format.animation.rate import Rate
from mpl_format.axes import AxesFormatter


class ShapeAnimation(object):

    @staticmethod
    def _float_anim(
            variable: Optional[StrOrFloatAnimation]
    ) -> Optional[FloatAnimation]:

        if isinstance(variable, str):
            variable = FloatAnimation(rate=variable)
        return variable

    def draw(self, t: float, axes: AxesFormatter):

        raise NotImplementedError

    def _add_non_animated_kwarg(self, arg_name: str, kwargs: dict):

        value = getattr(self, arg_name)
        if value is not None:
            kwargs[arg_name] = value

    def _add_color_kwarg(self, arg_name: str, kwargs: dict, t: float):

        value = getattr(self, arg_name)
        if value is not None:
            kwargs[arg_name] = (
                value.at(t) if isinstance(value, ColorAnimation)
                else value
            )

    def _add_float_kwarg(self, arg_name: str, kwargs: dict, t: float):

        value = getattr(self, arg_name)
        if value is not None:
            kwargs[arg_name] = (
                value.at(t) if isinstance(value, FloatAnimation)
                else Rate(value)(t) if isinstance(value, str)
                else value
            )
