'''_763.py

PinionConcave
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

_PINION_CONCAVE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'PinionConcave')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionConcave',)


class PinionConcave(_0.APIBase):
    '''PinionConcave

    This is a mastapy class.
    '''

    TYPE = _PINION_CONCAVE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionConcave.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pinion_cutter_parameters_concave(self) -> '_766.PinionFinishMachineSettings':
        '''PinionFinishMachineSettings: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _766.PinionFinishMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionFinishMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_cutter_parameters_concave_of_type_pinion_bevel_generating_modified_roll_machine_settings(self) -> '_761.PinionBevelGeneratingModifiedRollMachineSettings':
        '''PinionBevelGeneratingModifiedRollMachineSettings: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _761.PinionBevelGeneratingModifiedRollMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionBevelGeneratingModifiedRollMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_cutter_parameters_concave_of_type_pinion_bevel_generating_tilt_machine_settings(self) -> '_762.PinionBevelGeneratingTiltMachineSettings':
        '''PinionBevelGeneratingTiltMachineSettings: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _762.PinionBevelGeneratingTiltMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionBevelGeneratingTiltMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_cutter_parameters_concave_of_type_pinion_conical_machine_settings_specified(self) -> '_764.PinionConicalMachineSettingsSpecified':
        '''PinionConicalMachineSettingsSpecified: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _764.PinionConicalMachineSettingsSpecified.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionConicalMachineSettingsSpecified. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_cutter_parameters_concave_of_type_pinion_hypoid_formate_tilt_machine_settings(self) -> '_767.PinionHypoidFormateTiltMachineSettings':
        '''PinionHypoidFormateTiltMachineSettings: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _767.PinionHypoidFormateTiltMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionHypoidFormateTiltMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_cutter_parameters_concave_of_type_pinion_hypoid_generating_tilt_machine_settings(self) -> '_768.PinionHypoidGeneratingTiltMachineSettings':
        '''PinionHypoidGeneratingTiltMachineSettings: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _768.PinionHypoidGeneratingTiltMachineSettings.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionHypoidGeneratingTiltMachineSettings. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_cutter_parameters_concave_of_type_pinion_machine_settings_smt(self) -> '_769.PinionMachineSettingsSMT':
        '''PinionMachineSettingsSMT: 'PinionCutterParametersConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _769.PinionMachineSettingsSMT.TYPE not in self.wrapped.PinionCutterParametersConcave.__class__.__mro__:
            raise CastException('Failed to cast pinion_cutter_parameters_concave to PinionMachineSettingsSMT. Expected: {}.'.format(self.wrapped.PinionCutterParametersConcave.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PinionCutterParametersConcave.__class__)(self.wrapped.PinionCutterParametersConcave) if self.wrapped.PinionCutterParametersConcave is not None else None

    @property
    def pinion_concave_ob_configuration(self) -> '_783.BasicConicalGearMachineSettingsGenerated':
        '''BasicConicalGearMachineSettingsGenerated: 'PinionConcaveOBConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_783.BasicConicalGearMachineSettingsGenerated)(self.wrapped.PinionConcaveOBConfiguration) if self.wrapped.PinionConcaveOBConfiguration is not None else None
