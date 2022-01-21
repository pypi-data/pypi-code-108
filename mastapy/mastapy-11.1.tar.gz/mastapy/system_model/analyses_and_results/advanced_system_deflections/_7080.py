'''_7080.py

PowerLoadAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2213
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6657
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7114, _7116
from mastapy.system_model.analyses_and_results.system_deflections import _2527
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'PowerLoadAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadAdvancedSystemDeflection',)


class PowerLoadAdvancedSystemDeflection(_7116.VirtualComponentAdvancedSystemDeflection):
    '''PowerLoadAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6657.PowerLoadLoadCase':
        '''PowerLoadLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6657.PowerLoadLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def transmission_error_to_other_power_loads(self) -> 'List[_7114.TransmissionErrorToOtherPowerLoad]':
        '''List[TransmissionErrorToOtherPowerLoad]: 'TransmissionErrorToOtherPowerLoads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TransmissionErrorToOtherPowerLoads, constructor.new(_7114.TransmissionErrorToOtherPowerLoad))
        return value

    @property
    def component_system_deflection_results(self) -> 'List[_2527.PowerLoadSystemDeflection]':
        '''List[PowerLoadSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2527.PowerLoadSystemDeflection))
        return value
