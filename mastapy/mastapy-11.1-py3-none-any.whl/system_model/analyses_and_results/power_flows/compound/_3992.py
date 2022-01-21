'''_3992.py

RootAssemblyCompoundPowerFlow
'''


from typing import List

from mastapy.system_model.analyses_and_results.load_case_groups import (
    _5385, _5383, _5388, _5389,
    _5392
)
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.power_flows import _3862
from mastapy.system_model.analyses_and_results.power_flows.compound import _3905
from mastapy._internal.python_net import python_net_import

_ROOT_ASSEMBLY_COMPOUND_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound', 'RootAssemblyCompoundPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('RootAssemblyCompoundPowerFlow',)


class RootAssemblyCompoundPowerFlow(_3905.AssemblyCompoundPowerFlow):
    '''RootAssemblyCompoundPowerFlow

    This is a mastapy class.
    '''

    TYPE = _ROOT_ASSEMBLY_COMPOUND_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RootAssemblyCompoundPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def compound_static_load(self) -> '_5385.AbstractStaticLoadCaseGroup':
        '''AbstractStaticLoadCaseGroup: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5385.AbstractStaticLoadCaseGroup.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to AbstractStaticLoadCaseGroup. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad is not None else None

    @property
    def compound_static_load_of_type_abstract_design_state_load_case_group(self) -> '_5383.AbstractDesignStateLoadCaseGroup':
        '''AbstractDesignStateLoadCaseGroup: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5383.AbstractDesignStateLoadCaseGroup.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to AbstractDesignStateLoadCaseGroup. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad is not None else None

    @property
    def compound_static_load_of_type_design_state(self) -> '_5388.DesignState':
        '''DesignState: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5388.DesignState.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to DesignState. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad is not None else None

    @property
    def compound_static_load_of_type_duty_cycle(self) -> '_5389.DutyCycle':
        '''DutyCycle: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5389.DutyCycle.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to DutyCycle. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad is not None else None

    @property
    def compound_static_load_of_type_sub_group_in_single_design_state(self) -> '_5392.SubGroupInSingleDesignState':
        '''SubGroupInSingleDesignState: 'CompoundStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5392.SubGroupInSingleDesignState.TYPE not in self.wrapped.CompoundStaticLoad.__class__.__mro__:
            raise CastException('Failed to cast compound_static_load to SubGroupInSingleDesignState. Expected: {}.'.format(self.wrapped.CompoundStaticLoad.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CompoundStaticLoad.__class__)(self.wrapped.CompoundStaticLoad) if self.wrapped.CompoundStaticLoad is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3862.RootAssemblyPowerFlow]':
        '''List[RootAssemblyPowerFlow]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3862.RootAssemblyPowerFlow))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3862.RootAssemblyPowerFlow]':
        '''List[RootAssemblyPowerFlow]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3862.RootAssemblyPowerFlow))
        return value

    def set_face_widths_for_specified_safety_factors(self):
        ''' 'SetFaceWidthsForSpecifiedSafetyFactors' is the original name of this method.'''

        self.wrapped.SetFaceWidthsForSpecifiedSafetyFactors()
