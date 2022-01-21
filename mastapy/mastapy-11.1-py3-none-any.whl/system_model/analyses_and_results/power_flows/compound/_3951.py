'''_3951.py

FaceGearCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.part_model.gears import _2268
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.power_flows import _3820
from mastapy.system_model.analyses_and_results.power_flows.compound import _3956
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'FaceGearCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearCompoundPowerFlow',)


class FaceGearCompoundPowerFlow(_3956.GearCompoundPowerFlow):
    '''FaceGearCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2268.FaceGear':
        '''FaceGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2268.FaceGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_3820.FaceGearPowerFlow]':
        '''List[FaceGearPowerFlow]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3820.FaceGearPowerFlow))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3820.FaceGearPowerFlow]':
        '''List[FaceGearPowerFlow]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3820.FaceGearPowerFlow))
        return value
