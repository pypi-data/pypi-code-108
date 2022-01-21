'''_41.py

StressMeasurementShaftAxialBendingTorsionalComponentValues
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_STRESS_MEASUREMENT_SHAFT_AXIAL_BENDING_TORSIONAL_COMPONENT_VALUES = python_net_import('SMT.MastaAPI.Shafts', 'StressMeasurementShaftAxialBendingTorsionalComponentValues')


__docformat__ = 'restructuredtext en'
__all__ = ('StressMeasurementShaftAxialBendingTorsionalComponentValues',)


class StressMeasurementShaftAxialBendingTorsionalComponentValues(_0.APIBase):
    '''StressMeasurementShaftAxialBendingTorsionalComponentValues

    This is a mastapy class.
    '''

    TYPE = _STRESS_MEASUREMENT_SHAFT_AXIAL_BENDING_TORSIONAL_COMPONENT_VALUES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StressMeasurementShaftAxialBendingTorsionalComponentValues.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial(self) -> 'float':
        '''float: 'Axial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Axial

    @property
    def bending(self) -> 'float':
        '''float: 'Bending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Bending

    @property
    def torsional(self) -> 'float':
        '''float: 'Torsional' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Torsional
