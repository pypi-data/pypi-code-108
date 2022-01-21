'''_89.py

AngleInputComponent
'''


from mastapy._internal import constructor
from mastapy.nodal_analysis.varying_input_components import _88
from mastapy._internal.python_net import python_net_import

_ANGLE_INPUT_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.VaryingInputComponents', 'AngleInputComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('AngleInputComponent',)


class AngleInputComponent(_88.AbstractVaryingInputComponent):
    '''AngleInputComponent

    This is a mastapy class.
    '''

    TYPE = _ANGLE_INPUT_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngleInputComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.'''

        return self.wrapped.Angle

    @angle.setter
    def angle(self, value: 'float'):
        self.wrapped.Angle = float(value) if value else 0.0
