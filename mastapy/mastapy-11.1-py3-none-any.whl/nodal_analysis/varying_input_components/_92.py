'''_92.py

NonDimensionalInputComponent
'''


from mastapy._internal import constructor
from mastapy.nodal_analysis.varying_input_components import _88
from mastapy._internal.python_net import python_net_import

_NON_DIMENSIONAL_INPUT_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.VaryingInputComponents', 'NonDimensionalInputComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('NonDimensionalInputComponent',)


class NonDimensionalInputComponent(_88.AbstractVaryingInputComponent):
    '''NonDimensionalInputComponent

    This is a mastapy class.
    '''

    TYPE = _NON_DIMENSIONAL_INPUT_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NonDimensionalInputComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def non_dimensional_quantity(self) -> 'float':
        '''float: 'NonDimensionalQuantity' is the original name of this property.'''

        return self.wrapped.NonDimensionalQuantity

    @non_dimensional_quantity.setter
    def non_dimensional_quantity(self, value: 'float'):
        self.wrapped.NonDimensionalQuantity = float(value) if value else 0.0
