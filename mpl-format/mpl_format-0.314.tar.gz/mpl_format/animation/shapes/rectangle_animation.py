from typing import Optional, Union

from mpl_format.animation.shapes.base import ShapeAnimation
from mpl_format.animation.type_animations import \
    ColorOrColorAnimation, FloatOrFloatAnimation, StrOrFloatOrFloatAnimation
from mpl_format.axes import AxesFormatter
from mpl_format.enums.join_style import JOIN_STYLE
from mpl_format.enums.cap_style import CAP_STYLE
from mpl_format.enums.line_style import LINE_STYLE


class RectangleAnimation(ShapeAnimation, object):

    def __init__(
            self,
            x_center: FloatOrFloatAnimation,
            y_center: FloatOrFloatAnimation,
            width: FloatOrFloatAnimation,
            height: FloatOrFloatAnimation,
            angle: FloatOrFloatAnimation = 0.0,
            alpha: Optional[StrOrFloatOrFloatAnimation] = None,
            cap_style: Optional[Union[str, CAP_STYLE]] = None,
            color: Optional[ColorOrColorAnimation] = None,
            edge_color: Optional[ColorOrColorAnimation] = None,
            face_color: Optional[ColorOrColorAnimation] = None,
            fill: bool = True,
            join_style: Optional[Union[str, JOIN_STYLE]] = None,
            label: Optional[str] = None,
            line_style: Optional[Union[str, LINE_STYLE]] = None,
            line_width: Optional[FloatOrFloatAnimation] = None,
    ):
        """
        Add a rectangle to the Axes.

        :param x_center: The center rectangle x-coordinate.
        :param y_center: The center rectangle y-coordinate.
        :param width: Rectangle width.
        :param height: Rectangle height.
        :param angle: Rotation in degrees anti-clockwise about xy (default=0.0)
        :param alpha: Opacity.
        :param cap_style: Cap style.
        :param color: Use to set both the edge-color and the face-color.
        :param edge_color: Edge color.
        :param face_color: Face color.
        :param fill: Whether to fill the rectangle.
        :param join_style: Join style.
        :param label: Label for the object in the legend.
        :param line_style: Line style for edge.
        :param line_width: Line width for edge.
        """
        self.x_center: FloatOrFloatAnimation = x_center
        self.y_center: FloatOrFloatAnimation = y_center
        self.width: FloatOrFloatAnimation = width
        self.height: FloatOrFloatAnimation = height
        self.angle: FloatOrFloatAnimation = angle
        self.alpha: FloatOrFloatAnimation = self._float_anim(alpha)
        self.cap_style: Optional[Union[str, CAP_STYLE]] = cap_style
        self.color: Optional[ColorOrColorAnimation] = color
        self.edge_color: Optional[ColorOrColorAnimation] = edge_color
        self.face_color: Optional[ColorOrColorAnimation] = face_color
        self.fill: bool = fill
        self.join_style: Optional[Union[str, JOIN_STYLE]] = join_style
        self.label: Optional[str] = label
        self.line_style: Optional[Union[str, LINE_STYLE]] = line_style
        self.line_width: Optional[FloatOrFloatAnimation] = line_width

    def draw(self, t: float, axes: AxesFormatter):

        kwargs = {}
        for float_kwarg in ('x_center', 'y_center',
                            'width', 'height', 'angle',
                            'alpha', 'line_width'):
            self._add_float_kwarg(float_kwarg, kwargs, t)
        for color_kwarg in ('color', 'edge_color', 'face_color'):
            self._add_color_kwarg(color_kwarg, kwargs, t)
        for kwarg in ('cap_style', 'fill', 'join_style', 'label', 'line_style'):
            self._add_non_animated_kwarg(kwarg, kwargs)

        axes.add_rectangle(**kwargs)
