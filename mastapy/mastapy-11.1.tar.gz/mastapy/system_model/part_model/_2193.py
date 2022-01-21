'''_2193.py

ExternalCADModel
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2186
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'ExternalCADModel')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModel',)


class ExternalCADModel(_2186.Component):
    '''ExternalCADModel

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def draw_two_sided(self) -> 'bool':
        '''bool: 'DrawTwoSided' is the original name of this property.'''

        return self.wrapped.DrawTwoSided

    @draw_two_sided.setter
    def draw_two_sided(self, value: 'bool'):
        self.wrapped.DrawTwoSided = bool(value) if value else False

    @property
    def opacity(self) -> 'float':
        '''float: 'Opacity' is the original name of this property.'''

        return self.wrapped.Opacity

    @opacity.setter
    def opacity(self, value: 'float'):
        self.wrapped.Opacity = float(value) if value else 0.0
