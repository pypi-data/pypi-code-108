'''_2648.py

GuideDxfModelCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2196
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2497
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2611
from mastapy._internal.python_net import python_net_import

_GUIDE_DXF_MODEL_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'GuideDxfModelCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideDxfModelCompoundSystemDeflection',)


class GuideDxfModelCompoundSystemDeflection(_2611.ComponentCompoundSystemDeflection):
    '''GuideDxfModelCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _GUIDE_DXF_MODEL_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideDxfModelCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2196.GuideDxfModel':
        '''GuideDxfModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2196.GuideDxfModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2497.GuideDxfModelSystemDeflection]':
        '''List[GuideDxfModelSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2497.GuideDxfModelSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2497.GuideDxfModelSystemDeflection]':
        '''List[GuideDxfModelSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2497.GuideDxfModelSystemDeflection))
        return value
