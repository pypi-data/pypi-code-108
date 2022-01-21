'''_6248.py

WormGearSetCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2292
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6246, _6247, _6183
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6119
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'WormGearSetCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetCompoundDynamicAnalysis',)


class WormGearSetCompoundDynamicAnalysis(_6183.GearSetCompoundDynamicAnalysis):
    '''WormGearSetCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2292.WormGearSet':
        '''WormGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2292.WormGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def worm_gears_compound_dynamic_analysis(self) -> 'List[_6246.WormGearCompoundDynamicAnalysis]':
        '''List[WormGearCompoundDynamicAnalysis]: 'WormGearsCompoundDynamicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGearsCompoundDynamicAnalysis, constructor.new(_6246.WormGearCompoundDynamicAnalysis))
        return value

    @property
    def worm_meshes_compound_dynamic_analysis(self) -> 'List[_6247.WormGearMeshCompoundDynamicAnalysis]':
        '''List[WormGearMeshCompoundDynamicAnalysis]: 'WormMeshesCompoundDynamicAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshesCompoundDynamicAnalysis, constructor.new(_6247.WormGearMeshCompoundDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_6119.WormGearSetDynamicAnalysis]':
        '''List[WormGearSetDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6119.WormGearSetDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6119.WormGearSetDynamicAnalysis]':
        '''List[WormGearSetDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6119.WormGearSetDynamicAnalysis))
        return value
