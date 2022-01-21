'''_2198.py

GuideModelUsage
'''


from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GUIDE_MODEL_USAGE = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'GuideModelUsage')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideModelUsage',)


class GuideModelUsage(_0.APIBase):
    '''GuideModelUsage

    This is a mastapy class.
    '''

    TYPE = _GUIDE_MODEL_USAGE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideModelUsage.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def alignment_method(self) -> 'GuideModelUsage.AlignmentOptions':
        '''AlignmentOptions: 'AlignmentMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AlignmentMethod)
        return constructor.new(GuideModelUsage.AlignmentOptions)(value) if value is not None else None

    @alignment_method.setter
    def alignment_method(self, value: 'GuideModelUsage.AlignmentOptions'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AlignmentMethod = value

    @property
    def force_monochrome(self) -> 'bool':
        '''bool: 'ForceMonochrome' is the original name of this property.'''

        return self.wrapped.ForceMonochrome

    @force_monochrome.setter
    def force_monochrome(self, value: 'bool'):
        self.wrapped.ForceMonochrome = bool(value) if value else False

    @property
    def rotation(self) -> 'float':
        '''float: 'Rotation' is the original name of this property.'''

        return self.wrapped.Rotation

    @rotation.setter
    def rotation(self, value: 'float'):
        self.wrapped.Rotation = float(value) if value else 0.0

    @property
    def origin_horizontal(self) -> 'float':
        '''float: 'OriginHorizontal' is the original name of this property.'''

        return self.wrapped.OriginHorizontal

    @origin_horizontal.setter
    def origin_horizontal(self, value: 'float'):
        self.wrapped.OriginHorizontal = float(value) if value else 0.0

    @property
    def origin_vertical(self) -> 'float':
        '''float: 'OriginVertical' is the original name of this property.'''

        return self.wrapped.OriginVertical

    @origin_vertical.setter
    def origin_vertical(self, value: 'float'):
        self.wrapped.OriginVertical = float(value) if value else 0.0

    @property
    def clipping_left(self) -> 'float':
        '''float: 'ClippingLeft' is the original name of this property.'''

        return self.wrapped.ClippingLeft

    @clipping_left.setter
    def clipping_left(self, value: 'float'):
        self.wrapped.ClippingLeft = float(value) if value else 0.0

    @property
    def clipping_right(self) -> 'float':
        '''float: 'ClippingRight' is the original name of this property.'''

        return self.wrapped.ClippingRight

    @clipping_right.setter
    def clipping_right(self, value: 'float'):
        self.wrapped.ClippingRight = float(value) if value else 0.0

    @property
    def clipping_bottom(self) -> 'float':
        '''float: 'ClippingBottom' is the original name of this property.'''

        return self.wrapped.ClippingBottom

    @clipping_bottom.setter
    def clipping_bottom(self, value: 'float'):
        self.wrapped.ClippingBottom = float(value) if value else 0.0

    @property
    def clipping_top(self) -> 'float':
        '''float: 'ClippingTop' is the original name of this property.'''

        return self.wrapped.ClippingTop

    @clipping_top.setter
    def clipping_top(self, value: 'float'):
        self.wrapped.ClippingTop = float(value) if value else 0.0

    @property
    def clip_drawing(self) -> 'bool':
        '''bool: 'ClipDrawing' is the original name of this property.'''

        return self.wrapped.ClipDrawing

    @clip_drawing.setter
    def clip_drawing(self, value: 'bool'):
        self.wrapped.ClipDrawing = bool(value) if value else False

    @property
    def layout(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'Layout' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.Layout) if self.wrapped.Layout is not None else None

    @layout.setter
    def layout(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.Layout = value
