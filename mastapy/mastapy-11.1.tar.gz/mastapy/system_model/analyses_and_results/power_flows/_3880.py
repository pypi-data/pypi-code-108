'''_3880.py

StraightBevelSunGearPowerFlow
'''


from mastapy.system_model.part_model.gears import _2290
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.power_flows import _3874
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_SUN_GEAR_POWER_FLOW = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'StraightBevelSunGearPowerFlow')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelSunGearPowerFlow',)


class StraightBevelSunGearPowerFlow(_3874.StraightBevelDiffGearPowerFlow):
    '''StraightBevelSunGearPowerFlow

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_SUN_GEAR_POWER_FLOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelSunGearPowerFlow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2290.StraightBevelSunGear':
        '''StraightBevelSunGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2290.StraightBevelSunGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
