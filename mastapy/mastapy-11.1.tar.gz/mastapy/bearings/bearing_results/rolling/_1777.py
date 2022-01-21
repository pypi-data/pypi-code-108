'''_1777.py

LoadedRollerBearingElement
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_results.rolling import _1817, _1763
from mastapy._internal.python_net import python_net_import

_LOADED_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedRollerBearingElement',)


class LoadedRollerBearingElement(_1763.LoadedElement):
    '''LoadedRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rib_load(self) -> 'float':
        '''float: 'RibLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RibLoad

    @property
    def element_tilt(self) -> 'float':
        '''float: 'ElementTilt' is the original name of this property.'''

        return self.wrapped.ElementTilt

    @element_tilt.setter
    def element_tilt(self, value: 'float'):
        self.wrapped.ElementTilt = float(value) if value else 0.0

    @property
    def maximum_normal_stress_inner(self) -> 'float':
        '''float: 'MaximumNormalStressInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressInner

    @property
    def maximum_normal_stress_outer(self) -> 'float':
        '''float: 'MaximumNormalStressOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressOuter

    @property
    def maximum_normal_edge_stress_outer(self) -> 'float':
        '''float: 'MaximumNormalEdgeStressOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalEdgeStressOuter

    @property
    def maximum_normal_edge_stress_inner(self) -> 'float':
        '''float: 'MaximumNormalEdgeStressInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalEdgeStressInner

    @property
    def maximum_depth_of_maximum_shear_stress_inner(self) -> 'float':
        '''float: 'MaximumDepthOfMaximumShearStressInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumDepthOfMaximumShearStressInner

    @property
    def maximum_depth_of_maximum_shear_stress_outer(self) -> 'float':
        '''float: 'MaximumDepthOfMaximumShearStressOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumDepthOfMaximumShearStressOuter

    @property
    def maximum_contact_width_inner(self) -> 'float':
        '''float: 'MaximumContactWidthInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactWidthInner

    @property
    def maximum_contact_width_outer(self) -> 'float':
        '''float: 'MaximumContactWidthOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactWidthOuter

    @property
    def maximum_shear_stress_inner(self) -> 'float':
        '''float: 'MaximumShearStressInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumShearStressInner

    @property
    def maximum_shear_stress_outer(self) -> 'float':
        '''float: 'MaximumShearStressOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumShearStressOuter

    @property
    def contact_length_inner(self) -> 'float':
        '''float: 'ContactLengthInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactLengthInner

    @property
    def contact_length_outer(self) -> 'float':
        '''float: 'ContactLengthOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactLengthOuter

    @property
    def results_at_roller_offsets(self) -> 'List[_1817.ResultsAtRollerOffset]':
        '''List[ResultsAtRollerOffset]: 'ResultsAtRollerOffsets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ResultsAtRollerOffsets, constructor.new(_1817.ResultsAtRollerOffset))
        return value
