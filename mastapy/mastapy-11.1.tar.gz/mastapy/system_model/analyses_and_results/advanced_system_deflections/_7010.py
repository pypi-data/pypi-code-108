'''_7010.py

BoltedJointAdvancedSystemDeflection
'''


from typing import List

from mastapy.system_model.part_model import _2185
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6545
from mastapy.system_model.analyses_and_results.system_deflections import _2444
from mastapy.system_model.analyses_and_results.advanced_system_deflections import _7091
from mastapy._internal.python_net import python_net_import

_BOLTED_JOINT_ADVANCED_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'BoltedJointAdvancedSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltedJointAdvancedSystemDeflection',)


class BoltedJointAdvancedSystemDeflection(_7091.SpecialisedAssemblyAdvancedSystemDeflection):
    '''BoltedJointAdvancedSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _BOLTED_JOINT_ADVANCED_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltedJointAdvancedSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2185.BoltedJoint)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6545.BoltedJointLoadCase':
        '''BoltedJointLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6545.BoltedJointLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def assembly_system_deflection_results(self) -> 'List[_2444.BoltedJointSystemDeflection]':
        '''List[BoltedJointSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2444.BoltedJointSystemDeflection))
        return value
