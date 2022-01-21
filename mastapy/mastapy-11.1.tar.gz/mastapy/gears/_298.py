'''_298.py

GearSetOptimiser
'''


from typing import Optional

from mastapy._internal import constructor
from mastapy.gears import _297
from mastapy import _7275, _0
from mastapy._internal.python_net import python_net_import

_INT_32 = python_net_import('System', 'Int32')
_BOOLEAN = python_net_import('System', 'Boolean')
_TASK_PROGRESS = python_net_import('SMT.MastaAPIUtility', 'TaskProgress')
_GEAR_SET_OPTIMISER = python_net_import('SMT.MastaAPI.Gears', 'GearSetOptimiser')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetOptimiser',)


class GearSetOptimiser(_0.APIBase):
    '''GearSetOptimiser

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_OPTIMISER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetOptimiser.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bending_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'BendingSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingSafetyFactorForWorstGear

    @property
    def contact_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'ContactSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactSafetyFactorForWorstGear

    @property
    def static_bending_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'StaticBendingSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticBendingSafetyFactorForWorstGear

    @property
    def static_contact_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'StaticContactSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticContactSafetyFactorForWorstGear

    @property
    def scuffing_safety_factor_flash_temperature_method_for_worst_gear(self) -> 'float':
        '''float: 'ScuffingSafetyFactorFlashTemperatureMethodForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingSafetyFactorFlashTemperatureMethodForWorstGear

    @property
    def scuffing_safety_factor_integral_method_for_worst_gear(self) -> 'float':
        '''float: 'ScuffingSafetyFactorIntegralMethodForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ScuffingSafetyFactorIntegralMethodForWorstGear

    @property
    def permanent_deformation_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'PermanentDeformationSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermanentDeformationSafetyFactorForWorstGear

    @property
    def crack_initiation_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'CrackInitiationSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrackInitiationSafetyFactorForWorstGear

    @property
    def fatigue_fracture_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'FatigueFractureSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueFractureSafetyFactorForWorstGear

    @property
    def micropitting_safety_factor_for_worst_gear(self) -> 'float':
        '''float: 'MicropittingSafetyFactorForWorstGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MicropittingSafetyFactorForWorstGear

    def perform_strength_optimisation(self, number_of_results: 'int', use_current_design_as_starting_point: Optional['bool'] = False) -> '_297.GearSetOptimisationResults':
        ''' 'PerformStrengthOptimisation' is the original name of this method.

        Args:
            number_of_results (int)
            use_current_design_as_starting_point (bool, optional)

        Returns:
            mastapy.gears.GearSetOptimisationResults
        '''

        number_of_results = int(number_of_results)
        use_current_design_as_starting_point = bool(use_current_design_as_starting_point)
        method_result = self.wrapped.PerformStrengthOptimisation.Overloads[_INT_32, _BOOLEAN](number_of_results if number_of_results else 0, use_current_design_as_starting_point if use_current_design_as_starting_point else False)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def perform_strength_optimisation_with_progress(self, number_of_results: 'int', progress: '_7275.TaskProgress', use_current_design_as_starting_point: Optional['bool'] = False) -> '_297.GearSetOptimisationResults':
        ''' 'PerformStrengthOptimisation' is the original name of this method.

        Args:
            number_of_results (int)
            progress (mastapy.TaskProgress)
            use_current_design_as_starting_point (bool, optional)

        Returns:
            mastapy.gears.GearSetOptimisationResults
        '''

        number_of_results = int(number_of_results)
        use_current_design_as_starting_point = bool(use_current_design_as_starting_point)
        method_result = self.wrapped.PerformStrengthOptimisation.Overloads[_INT_32, _TASK_PROGRESS, _BOOLEAN](number_of_results if number_of_results else 0, progress.wrapped if progress else None, use_current_design_as_starting_point if use_current_design_as_starting_point else False)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def dispose(self):
        ''' 'Dispose' is the original name of this method.'''

        self.wrapped.Dispose()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.dispose()
