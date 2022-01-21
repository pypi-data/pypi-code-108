'''_7176.py

FaceGearCompoundAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model.gears import _2268
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7045
from mastapy.system_model.analyses_and_results.advanced_system_deflections.compound import _7181
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections.Compound', 'FaceGearCompoundAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearCompoundAdvancedSystemDeflection',)


class FaceGearCompoundAdvancedSystemDeflection(_7181.GearCompoundAdvancedSystemDeflection):
    '''FaceGearCompoundAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearCompoundAdvancedSystemDeflection.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_7045.FaceGearAdvancedSystemDeflection]':
        '''List[FaceGearAdvancedSystemDeflection]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_7045.FaceGearAdvancedSystemDeflection))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_7045.FaceGearAdvancedSystemDeflection]':
        '''List[FaceGearAdvancedSystemDeflection]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_7045.FaceGearAdvancedSystemDeflection))
        return value
