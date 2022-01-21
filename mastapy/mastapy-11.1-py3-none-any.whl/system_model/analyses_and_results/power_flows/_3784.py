'''_3784.py

BoltedJointPowerFlow
'''


from mastapy.system_model.part_model import _2185
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6545
from mastapy.system_model.analyses_and_results.power_flows import _3866
from mastapy._internal.python_net import python_net_import

_BOLTED_JOINT_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'BoltedJointPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltedJointPowerFlow',)


class BoltedJointPowerFlow(_3866.SpecialisedAssemblyPowerFlow):
    '''BoltedJointPowerFlow

    This is a mastapy class.
    '''

    TYPE = _BOLTED_JOINT_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltedJointPowerFlow.TYPE'):
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
