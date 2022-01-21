'''_275.py

DrawStyle
'''


from mastapy._internal import constructor
from mastapy.geometry import _276
from mastapy._internal.python_net import python_net_import

_DRAW_STYLE = python_net_import('SMT.MastaAPI.Geometry', 'DrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('DrawStyle',)


class DrawStyle(_276.DrawStyleBase):
    '''DrawStyle

    This is a mastapy class.
    '''

    TYPE = _DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def outline_axis(self) -> 'bool':
        '''bool: 'OutlineAxis' is the original name of this property.'''

        return self.wrapped.OutlineAxis

    @outline_axis.setter
    def outline_axis(self, value: 'bool'):
        self.wrapped.OutlineAxis = bool(value) if value else False

    @property
    def show_part_labels(self) -> 'bool':
        '''bool: 'ShowPartLabels' is the original name of this property.'''

        return self.wrapped.ShowPartLabels

    @show_part_labels.setter
    def show_part_labels(self, value: 'bool'):
        self.wrapped.ShowPartLabels = bool(value) if value else False
