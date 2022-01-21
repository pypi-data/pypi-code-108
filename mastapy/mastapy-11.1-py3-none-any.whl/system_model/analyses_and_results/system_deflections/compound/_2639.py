'''_2639.py

ExternalCADModelCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2193
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections import _2487
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2611
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'ExternalCADModelCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModelCompoundSystemDeflection',)


class ExternalCADModelCompoundSystemDeflection(_2611.ComponentCompoundSystemDeflection):
    '''ExternalCADModelCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModelCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2193.ExternalCADModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_2487.ExternalCADModelSystemDeflection]':
        '''List[ExternalCADModelSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_2487.ExternalCADModelSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_2487.ExternalCADModelSystemDeflection]':
        '''List[ExternalCADModelSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_2487.ExternalCADModelSystemDeflection))
        return value
