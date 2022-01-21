'''_765.py

PinionConvex
'''


from mastapy.gears.manufacturing.bevel import (
    _766, _761, _762, _764,
    _767, _768, _769
)
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.bevel.basic_machine_settings import _783
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PINION_CONVEX = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'PinionConvex')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionConvex',)


class PinionConvex(_0.APIBase):
    '''PinionConvex

    This is a mastapy class.
    '''

    TYPE = _PINION_CONVEX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionConvex.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pinion_cutter_parameters_convex(self) -> '_766.PinionFinishMachineSettings':
        '''PinionFinishMachineSettings: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _766.PinionFinishMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionFinishMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_cutter_parameters_convex_of_type_pinion_bevel_generating_modified_roll_machine_settings(self) -> '_761.PinionBevelGeneratingModifiedRollMachineSettings':
        '''PinionBevelGeneratingModifiedRollMachineSettings: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _761.PinionBevelGeneratingModifiedRollMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionBevelGeneratingModifiedRollMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_cutter_parameters_convex_of_type_pinion_bevel_generating_tilt_machine_settings(self) -> '_762.PinionBevelGeneratingTiltMachineSettings':
        '''PinionBevelGeneratingTiltMachineSettings: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _762.PinionBevelGeneratingTiltMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionBevelGeneratingTiltMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_cutter_parameters_convex_of_type_pinion_conical_machine_settings_specified(self) -> '_764.PinionConicalMachineSettingsSpecified':
        '''PinionConicalMachineSettingsSpecified: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _764.PinionConicalMachineSettingsSpecified.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionConicalMachineSettingsSpecified. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_cutter_parameters_convex_of_type_pinion_hypoid_formate_tilt_machine_settings(self) -> '_767.PinionHypoidFormateTiltMachineSettings':
        '''PinionHypoidFormateTiltMachineSettings: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _767.PinionHypoidFormateTiltMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionHypoidFormateTiltMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_cutter_parameters_convex_of_type_pinion_hypoid_generating_tilt_machine_settings(self) -> '_768.PinionHypoidGeneratingTiltMachineSettings':
        '''PinionHypoidGeneratingTiltMachineSettings: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _768.PinionHypoidGeneratingTiltMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionHypoidGeneratingTiltMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_cutter_parameters_convex_of_type_pinion_machine_settings_smt(self) -> '_769.PinionMachineSettingsSMT':
        '''PinionMachineSettingsSMT: 'PinionCutterParametersConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _769.PinionMachineSettingsSMT.TYPE not in self.wrapped.PinionCutterParametersConvex.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_convex to PinionMachineSettingsSMT. Expected: {}.'.format(self.wrapped.PinionCutterParametersConvex.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConvex.__class__)(self.wrapped.PinionCutterParametersConvex) if self.wrapped.PinionCutterParametersConvex is not None else None

    @property
    def pinion_convex_ib_configuration(self) -> '_783.BasicConicalGearMachineSettingsGenerated':
        '''BasicConicalGearMachineSettingsGenerated: 'PinionConvexIBConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_783.BasicConicalGearMachineSettingsGenerated)(self.wrapped.PinionConvexIBConfiguration) if self.wrapped.PinionConvexIBConfiguration is not None else None
