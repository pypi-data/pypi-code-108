'''_7115.py

UnbalancedMassAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6699
from mastapy.system_model.analyses_and_results.system_deflections import _2569
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7116
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'UnbalancedMassAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassAdvancedSystemDeflection',)


class UnbalancedMassAdvancedSystemDeflection(_7116.VirtualComponentAdvancedSystemDeflection):
    '''UnbalancedMassAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6699.UnbalancedMassLoadCase':
        '''UnbalancedMassLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6699.UnbalancedMassLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_system_deflection_results(self) -> 'List[_2569.UnbalancedMassSystemDeflection]':
        '''List[UnbalancedMassSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2569.UnbalancedMassSystemDeflection))
        return value
