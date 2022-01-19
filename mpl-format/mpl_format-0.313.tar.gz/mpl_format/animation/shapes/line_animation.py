from typing import Union, Optional

from numpy import linspace
from scipy.interpolate import interp1d

from compound_types.built_ins import FloatIterable
from mpl_format.animation.kwarg_animations.float_animation import FloatAnimation
from mpl_format.animation.shapes.base import ShapeAnimation
from mpl_format.animation.type_animations import \
    FloatOrFloatAnimation, ColorOrColorAnimation, StrOrFloatAnimation, \
    StrOrFloatOrFloatAnimation
from mpl_format.axes import AxesFormatter
from mpl_format.enums.marker_style import MARKER_STYLE
from mpl_format.enums.draw_style import DRAW_STYLE
from mpl_format.enums.line_style import LINE_STYLE


class LineAnimation(ShapeAnimation, object):

    def __init__(
            self,
            x: FloatIterable,
            y: FloatIterable,
            smooth: Union[bool, int] = False,
            smooth_order: int = 2,
            length: Optional[StrOrFloatAnimation] = None,
            alpha: Optional[StrOrFloatOrFloatAnimation] = None,
            color: Optional[ColorOrColorAnimation] = None,
            draw_style: Optional[Union[str, DRAW_STYLE]] = None,
            label: Optional[str] = None,
            line_style: Optional[Union[str, LINE_STYLE]] = None,
            line_width: Optional[FloatOrFloatAnimation] = None,
            marker: Optional[Union[str, MARKER_STYLE]] = None,
            marker_edge_color: Optional[ColorOrColorAnimation] = None,
            marker_edge_width: Optional[FloatOrFloatAnimation] = None,
            marker_face_color: Optional[ColorOrColorAnimation] = None,
            marker_face_color_alt: Optional[ColorOrColorAnimation] = None,
            marker_size: Optional[FloatOrFloatAnimation] = None
    ):
        if smooth is not False:
            if smooth is True:
                smooth = 1000
            f_smooth = interp1d(x, y, kind=smooth_order)
            x_smooth = linspace(min(x), max(x), smooth)
            y_smooth = f_smooth(x_smooth)
            x = x_smooth
            y = y_smooth
        self.x: FloatIterable = x
        self.y: FloatIterable = y
        self.length: Optional[FloatAnimation] = self._float_anim(length)
        self.alpha: FloatOrFloatAnimation = self._float_anim(alpha)
        self.color: Optional[ColorOrColorAnimation] = color
        self.draw_style: Optional[Union[str, DRAW_STYLE]] = draw_style
        self.label: Optional[str] = label
        self.line_style: Optional[Union[str, LINE_STYLE]] = line_style
        self.line_width: Optional[FloatOrFloatAnimation] = line_width
        self.marker: Optional[Union[str, MARKER_STYLE]] = marker
        self.marker_edge_color: Optional[ColorOrColorAnimation] = \
            marker_edge_color
        self.marker_edge_width: Optional[FloatOrFloatAnimation] = \
            marker_edge_width
        self.marker_face_color: Optional[ColorOrColorAnimation] = \
            marker_face_color
        self.marker_face_color_alt: Optional[ColorOrColorAnimation] = \
            marker_face_color_alt
        self.marker_size: Optional[FloatOrFloatAnimation] = marker_size

    def draw(self, t: float, axes: AxesFormatter):

        kwargs = {}

        if self.length is not None:
            kwargs['x'] = self.x[: int(round(self.length.at(t) * len(self.x)))]
            kwargs['y'] = self.y[: int(round(self.length.at(t) * len(self.y)))]
        else:
            kwargs['x'] = self.x
            kwargs['y'] = self.y
        for float_kwarg in ('alpha', 'line_width',
                            'marker_edge_width', 'marker_size'):
            self._add_float_kwarg(float_kwarg, kwargs, t)
        for color_kwarg in ('color', 'marker_edge_color',
                            'marker_face_color', 'marker_face_color_alt'):
            self._add_color_kwarg(color_kwarg, kwargs, t)
        for kwarg in ('draw_style', 'label', 'line_style', 'marker'):
            self._add_non_animated_kwarg(kwarg, kwargs)

        axes.add_line(**kwargs)
