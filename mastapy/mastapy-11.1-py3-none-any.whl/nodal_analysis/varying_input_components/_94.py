'''_94.py

VelocityInputComponent
'''


from mastapy._internal import constructor
from mastapy.nodal_analysis.varying_input_components import _88
from mastapy._internal.python_net import python_net_import

_VELOCITY_INPUT_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.VaryingInputComponents', 'VelocityInputComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('VelocityInputComponent',)


class VelocityInputComponent(_88.AbstractVaryingInputComponent):
    '''VelocityInputComponent

    This is a mastapy class.
    '''

    TYPE = _VELOCITY_INPUT_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VelocityInputComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def velocity(self) -> 'float':
        '''float: 'Velocity' is the original name of this property.'''

        return self.wrapped.Velocity

    @velocity.setter
    def velocity(self, value: 'float'):
        self.wrapped.Velocity = float(value) if value else 0.0
