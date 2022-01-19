from typing import Optional, Union

from mpl_format.animation.kwarg_animations import FloatAnimation
from mpl_format.animation.shapes.base import ShapeAnimation
from mpl_format.animation.type_animations import FloatOrFloatAnimation, \
    StrOrFloatAnimation, ColorOrColorAnimation
from mpl_format.compound_types import Color
from mpl_format.enums import FONT_SIZE, FONT_STRETCH, FONT_STYLE, \
    FONT_VARIANT, FONT_WEIGHT, CAP_STYLE, JOIN_STYLE, LINE_STYLE


class TextAnimation(ShapeAnimation, object):

    def __init__(
            self, x: FloatOrFloatAnimation,
            y: FloatOrFloatAnimation,
            text: str,
            length: Optional[StrOrFloatAnimation] = None,
            font_dict: Optional[dict] = None,
            alpha: Optional[float] = None,
            color: Optional[ColorOrColorAnimation] = None,
            h_align: Optional[str] = None,
            v_align: Optional[str] = None,
            m_align: Optional[str] = None,
            line_spacing: Optional[float] = None,
            font_family: Optional[str] = None,
            font_size: Optional[Union[int, float, str, FONT_SIZE]] = None,
            font_stretch: Optional[Union[int, float, FONT_STRETCH]] = None,
            font_style: Optional[Union[str, FONT_STYLE]] = None,
            font_variant: Optional[Union[str, FONT_VARIANT]] = None,
            font_weight: Optional[Union[int, float, str, FONT_WEIGHT]] = None,
            wrap: Optional[bool] = None,
            bbox_style: Optional[str] = None,
            bbox_alpha: Optional[float] = None,
            bbox_cap_style: Optional[Union[str, CAP_STYLE]] = None,
            bbox_color: Optional[Color] = None,
            bbox_edge_color: Optional[Color] = None,
            bbox_face_color: Optional[Color] = None,
            bbox_fill: Optional[bool] = None,
            bbox_join_style: Optional[Union[str, JOIN_STYLE]] = None,
            bbox_line_style: Optional[Union[str, LINE_STYLE]] = None,
            bbox_line_width: Optional[float] = None
    ):
        self.x: FloatOrFloatAnimation = x
        self.y: FloatOrFloatAnimation = y
        self.text: str = text
        self.length: Optional[FloatAnimation] = self._float_anim(length)
        self.font_dict: Optional[dict] = font_dict
        self.alpha: FloatOrFloatAnimation = self._float_anim(alpha)
        self.color: Optional[ColorOrColorAnimation] = color
        self.h_align: Optional[str] = h_align
        self.v_align: Optional[str] = v_align
        self.m_align: Optional[str] = m_align
        self.line_spacing: Optional[float] = line_spacing
        self.font_family: Optional[str] = font_family
        self.font_size: Optional[Union[int, float, str, FONT_SIZE]] = font_size
        self.font_stretch: Optional[
            Union[int, float, FONT_STRETCH]] = font_stretch
        self.font_style: Optional[Union[str, FONT_STYLE]] = font_style
        self.font_variant: Optional[Union[str, FONT_VARIANT]] = font_variant
        self.font_weight: Optional[
            Union[int, float, str, FONT_WEIGHT]] = font_weight
        self.wrap: Optional[bool] = wrap
        self.bbox_style: Optional[str] = bbox_style
        self.bbox_alpha: Optional[float] = bbox_alpha
        self.bbox_cap_style: Optional[Union[str, CAP_STYLE]] = bbox_cap_style
        self.bbox_color: Optional[Color] = bbox_color
        self.bbox_edge_color: Optional[Color] = bbox_edge_color
        self.bbox_face_color: Optional[Color] = bbox_face_color
        self.bbox_fill: Optional[bool] = bbox_fill
        self.bbox_join_style: Optional[Union[str, JOIN_STYLE]] = bbox_join_style
        self.bbox_line_style: Optional[Union[str, LINE_STYLE]] = bbox_line_style
        self.bbox_line_width: Optional[float] = bbox_line_width

    # def draw(self, t: float, axes: AxesFormatter):
    #
    #     kwargs = {}
    #
    #     if self.length is not None:
    #         num_chars = int(len(self.text) * self.length.at(t))
    #         kwargs['text'] = self.text[: num_chars]
    #     else:
    #         kwargs['text'] = self.text
    #
    #     for float_kwarg in ('x', 'y', '')
