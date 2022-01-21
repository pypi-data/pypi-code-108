'''_6170.py

CylindricalGearCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.gears import _2265, _2267
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6040
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6181
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'CylindricalGearCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearCompoundDynamicAnalysis',)


class CylindricalGearCompoundDynamicAnalysis(_6181.GearCompoundDynamicAnalysis):
    '''CylindricalGearCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2265.CylindricalGear':
        '''CylindricalGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2265.CylindricalGear.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalGear. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6040.CylindricalGearDynamicAnalysis]':
        '''List[CylindricalGearDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6040.CylindricalGearDynamicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[CylindricalGearCompoundDynamicAnalysis]':
        '''List[CylindricalGearCompoundDynamicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(CylindricalGearCompoundDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6040.CylindricalGearDynamicAnalysis]':
        '''List[CylindricalGearDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6040.CylindricalGearDynamicAnalysis))
        return value
