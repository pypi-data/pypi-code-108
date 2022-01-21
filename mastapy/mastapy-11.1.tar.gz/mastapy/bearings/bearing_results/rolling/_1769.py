'''_1769.py

LoadedNeedleRollerBearingElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1757
from mastapy._internal.python_net import python_net_import

_LOADED_NEEDLE_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedNeedleRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedNeedleRollerBearingElement',)


class LoadedNeedleRollerBearingElement(_1757.LoadedCylindricalRollerBearingElement):
    '''LoadedNeedleRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_NEEDLE_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedNeedleRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sliding_power_loss_from_macro_sliding_due_to_roller_skew(self) -> 'float':
        '''float: 'SlidingPowerLossFromMacroSlidingDueToRollerSkew' is the original name of this property.'''

        return self.wrapped.SlidingPowerLossFromMacroSlidingDueToRollerSkew

    @sliding_power_loss_from_macro_sliding_due_to_roller_skew.setter
    def sliding_power_loss_from_macro_sliding_due_to_roller_skew(self, value: 'float'):
        self.wrapped.SlidingPowerLossFromMacroSlidingDueToRollerSkew = float(value) if value else 0.0

    @property
    def sliding_power_loss_from_hysteresis(self) -> 'float':
        '''float: 'SlidingPowerLossFromHysteresis' is the original name of this property.'''

        return self.wrapped.SlidingPowerLossFromHysteresis

    @sliding_power_loss_from_hysteresis.setter
    def sliding_power_loss_from_hysteresis(self, value: 'float'):
        self.wrapped.SlidingPowerLossFromHysteresis = float(value) if value else 0.0

    @property
    def sliding_power_loss_roller_cage_moment_component(self) -> 'float':
        '''float: 'SlidingPowerLossRollerCageMomentComponent' is the original name of this property.'''

        return self.wrapped.SlidingPowerLossRollerCageMomentComponent

    @sliding_power_loss_roller_cage_moment_component.setter
    def sliding_power_loss_roller_cage_moment_component(self, value: 'float'):
        self.wrapped.SlidingPowerLossRollerCageMomentComponent = float(value) if value else 0.0

    @property
    def sliding_power_loss_roller_cage_radial_component(self) -> 'float':
        '''float: 'SlidingPowerLossRollerCageRadialComponent' is the original name of this property.'''

        return self.wrapped.SlidingPowerLossRollerCageRadialComponent

    @sliding_power_loss_roller_cage_radial_component.setter
    def sliding_power_loss_roller_cage_radial_component(self, value: 'float'):
        self.wrapped.SlidingPowerLossRollerCageRadialComponent = float(value) if value else 0.0

    @property
    def sliding_power_loss_roller_cage_axial_component(self) -> 'float':
        '''float: 'SlidingPowerLossRollerCageAxialComponent' is the original name of this property.'''

        return self.wrapped.SlidingPowerLossRollerCageAxialComponent

    @sliding_power_loss_roller_cage_axial_component.setter
    def sliding_power_loss_roller_cage_axial_component(self, value: 'float'):
        self.wrapped.SlidingPowerLossRollerCageAxialComponent = float(value) if value else 0.0
