'''_2604.py

BevelGearSetCompoundSystemDeflection
'''


from typing import List

from mastapy.system_model.analyses_and_results.system_deflections import _2442
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.system_deflections.compound import _2592
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'BevelGearSetCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSetCompoundSystemDeflection',)


class BevelGearSetCompoundSystemDeflection(_2592.AGMAGleasonConicalGearSetCompoundSystemDeflection):
    '''BevelGearSetCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSetCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_2442.BevelGearSetSystemDeflection]':
        '''List[BevelGearSetSystemDeflection]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_2442.BevelGearSetSystemDeflection))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_2442.BevelGearSetSystemDeflection]':
        '''List[BevelGearSetSystemDeflection]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_2442.BevelGearSetSystemDeflection))
        return value
