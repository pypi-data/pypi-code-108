'''_90.py

ForceInputComponent
'''


from mastapy._internal import constructor
from mastapy.nodal_analysis.varying_input_components import _88
from mastapy._internal.python_net import python_net_import

_FORCE_INPUT_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.VaryingInputComponents', 'ForceInputComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('ForceInputComponent',)


class ForceInputComponent(_88.AbstractVaryingInputComponent):
    '''ForceInputComponent

    This is a mastapy class.
    '''

    TYPE = _FORCE_INPUT_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ForceInputComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def force(self) -> 'float':
        '''float: 'Force' is the original name of this property.'''

        return self.wrapped.Force

    @force.setter
    def force(self, value: 'float'):
        self.wrapped.Force = float(value) if value else 0.0
