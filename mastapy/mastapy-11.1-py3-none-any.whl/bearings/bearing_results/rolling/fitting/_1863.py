'''_1863.py

RingFittingThermalResults
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_results.rolling.fitting import _1861
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RING_FITTING_THERMAL_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.Fitting', 'RingFittingThermalResults')


__docformat__ = 'restructuredtext en'
__all__ = ('RingFittingThermalResults',)


class RingFittingThermalResults(_0.APIBase):
    '''RingFittingThermalResults

    This is a mastapy class.
    '''

    TYPE = _RING_FITTING_THERMAL_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingFittingThermalResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def interfacial_normal_stress(self) -> 'float':
        '''float: 'InterfacialNormalStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InterfacialNormalStress

    @property
    def maximum_hoop_stress(self) -> 'float':
        '''float: 'MaximumHoopStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumHoopStress

    @property
    def change_in_diameter_due_to_interference_and_centrifugal_effects(self) -> 'float':
        '''float: 'ChangeInDiameterDueToInterferenceAndCentrifugalEffects' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInDiameterDueToInterferenceAndCentrifugalEffects

    @property
    def interfacial_clearance_included_in_analysis(self) -> 'bool':
        '''bool: 'InterfacialClearanceIncludedInAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InterfacialClearanceIncludedInAnalysis

    @property
    def interference_values(self) -> 'List[_1861.InterferenceComponents]':
        '''List[InterferenceComponents]: 'InterferenceValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InterferenceValues, constructor.new(_1861.InterferenceComponents))
        return value
