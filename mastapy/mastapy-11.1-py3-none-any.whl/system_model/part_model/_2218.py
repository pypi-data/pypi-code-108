'''_2218.py

UnbalancedMass
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2220
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'UnbalancedMass')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMass',)


class UnbalancedMass(_2220.VirtualComponent):
    '''UnbalancedMass

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMass.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.'''

        return self.wrapped.Angle

    @angle.setter
    def angle(self, value: 'float'):
        self.wrapped.Angle = float(value) if value else 0.0
