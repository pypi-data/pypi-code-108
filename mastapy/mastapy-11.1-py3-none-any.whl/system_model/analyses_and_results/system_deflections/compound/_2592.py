'''_2592.py

AGMAGleasonConicalGearSetCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2430
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2620
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'AGMAGleasonConicalGearSetCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearSetCompoundSystemDeflection',)


class AGMAGleasonConicalGearSetCompoundSystemDeflection(_2620.ConicalGearSetCompoundSystemDeflection):
    '''AGMAGleasonConicalGearSetCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearSetCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_2430.AGMAGleasonConicalGearSetSystemDeflection]':
        '''List[AGMAGleasonConicalGearSetSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2430.AGMAGleasonConicalGearSetSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2430.AGMAGleasonConicalGearSetSystemDeflection]':
        '''List[AGMAGleasonConicalGearSetSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2430.AGMAGleasonConicalGearSetSystemDeflection))
        return value
