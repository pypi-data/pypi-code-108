'''_68.py

LinearDampingConnectionProperties
'''


from mastapy._internal import constructor
from mastapy.nodal_analysis import _43
from mastapy._internal.python_net import python_net_import

_LINEAR_DAMPING_CONNECTION_PROPERTIES = python_net_import('SMT.MastaAPI.NodalAnalysis', 'LinearDampingConnectionProperties')


__docformat__ = 'restructuredtext en'
__all__ = ('LinearDampingConnectionProperties',)


class LinearDampingConnectionProperties(_43.AbstractLinearConnectionProperties):
    '''LinearDampingConnectionProperties

    This is a mastapy class.
    '''

    TYPE = _LINEAR_DAMPING_CONNECTION_PROPERTIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LinearDampingConnectionProperties.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def torsional_damping(self) -> 'float':
        '''float: 'TorsionalDamping' is the original name of this property.'''

        return self.wrapped.TorsionalDamping

    @torsional_damping.setter
    def torsional_damping(self, value: 'float'):
        self.wrapped.TorsionalDamping = float(value) if value else 0.0

    @property
    def radial_damping(self) -> 'float':
        '''float: 'RadialDamping' is the original name of this property.'''

        return self.wrapped.RadialDamping

    @radial_damping.setter
    def radial_damping(self, value: 'float'):
        self.wrapped.RadialDamping = float(value) if value else 0.0

    @property
    def axial_damping(self) -> 'float':
        '''float: 'AxialDamping' is the original name of this property.'''

        return self.wrapped.AxialDamping

    @axial_damping.setter
    def axial_damping(self, value: 'float'):
        self.wrapped.AxialDamping = float(value) if value else 0.0

    @property
    def tilt_damping(self) -> 'float':
        '''float: 'TiltDamping' is the original name of this property.'''

        return self.wrapped.TiltDamping

    @tilt_damping.setter
    def tilt_damping(self, value: 'float'):
        self.wrapped.TiltDamping = float(value) if value else 0.0
