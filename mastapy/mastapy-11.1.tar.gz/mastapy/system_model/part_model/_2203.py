'''_2203.py

MassDisc
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2220
from mastapy._internal.python_net import python_net_import

_MASS_DISC = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'MassDisc')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDisc',)


class MassDisc(_2220.VirtualComponent):
    '''MassDisc

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDisc.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def density(self) -> 'float':
        '''float: 'Density' is the original name of this property.'''

        return self.wrapped.Density

    @density.setter
    def density(self, value: 'float'):
        self.wrapped.Density = float(value) if value else 0.0

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def is_distributed(self) -> 'bool':
        '''bool: 'IsDistributed' is the original name of this property.'''

        return self.wrapped.IsDistributed

    @is_distributed.setter
    def is_distributed(self, value: 'bool'):
        self.wrapped.IsDistributed = bool(value) if value else False

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

    @property
    def inner_diameter(self) -> 'float':
        '''float: 'InnerDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerDiameter

    @property
    def disc_skew(self) -> 'float':
        '''float: 'DiscSkew' is the original name of this property.'''

        return self.wrapped.DiscSkew

    @disc_skew.setter
    def disc_skew(self, value: 'float'):
        self.wrapped.DiscSkew = float(value) if value else 0.0

    @property
    def disc_rotation(self) -> 'float':
        '''float: 'DiscRotation' is the original name of this property.'''

        return self.wrapped.DiscRotation

    @disc_rotation.setter
    def disc_rotation(self, value: 'float'):
        self.wrapped.DiscRotation = float(value) if value else 0.0
