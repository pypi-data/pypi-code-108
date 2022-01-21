'''_679.py

VirtualSimulationCalculator
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.cutter_simulation import _663
from mastapy._internal.python_net import python_net_import

_VIRTUAL_SIMULATION_CALCULATOR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'VirtualSimulationCalculator')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualSimulationCalculator',)


class VirtualSimulationCalculator(_663.CutterSimulationCalc):
    '''VirtualSimulationCalculator

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_SIMULATION_CALCULATOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualSimulationCalculator.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending_moment_arm_for_iso_rating_worst(self) -> 'float':
        '''float: 'BendingMomentArmForISORatingWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingMomentArmForISORatingWorst

    @property
    def radius_of_critical_point_for_iso_rating_worst(self) -> 'float':
        '''float: 'RadiusOfCriticalPointForISORatingWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusOfCriticalPointForISORatingWorst

    @property
    def tooth_root_chord_for_iso_rating_worst(self) -> 'float':
        '''float: 'ToothRootChordForISORatingWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordForISORatingWorst

    @property
    def root_fillet_radius_for_iso_rating_worst(self) -> 'float':
        '''float: 'RootFilletRadiusForISORatingWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForISORatingWorst

    @property
    def tooth_root_chord_for_iso_rating(self) -> 'float':
        '''float: 'ToothRootChordForISORating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothRootChordForISORating

    @property
    def root_fillet_radius_for_iso_rating(self) -> 'float':
        '''float: 'RootFilletRadiusForISORating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForISORating

    @property
    def root_fillet_radius_for_agma_rating(self) -> 'float':
        '''float: 'RootFilletRadiusForAGMARating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusForAGMARating

    @property
    def form_factor_for_iso_rating_worst(self) -> 'float':
        '''float: 'FormFactorForISORatingWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormFactorForISORatingWorst

    @property
    def stress_correction_factor_for_iso_rating_worst(self) -> 'float':
        '''float: 'StressCorrectionFactorForISORatingWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFactorForISORatingWorst

    @property
    def stress_correction_form_factor_worst(self) -> 'float':
        '''float: 'StressCorrectionFormFactorWorst' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressCorrectionFormFactorWorst
