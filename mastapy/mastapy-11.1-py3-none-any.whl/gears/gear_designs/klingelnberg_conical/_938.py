'''_938.py

KlingelnbergConicalGearDesign
'''


from mastapy._internal.python_net import python_net_import
from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.materials import _561
from mastapy.gears.gear_designs.conical import _1101

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_KLINGELNBERG_CONICAL_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergConical', 'KlingelnbergConicalGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergConicalGearDesign',)


class KlingelnbergConicalGearDesign(_1101.ConicalGearDesign):
    '''KlingelnbergConicalGearDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CONICAL_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergConicalGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def material(self) -> 'str':
        '''str: 'Material' is the original name of this property.'''

        return self.wrapped.Material.SelectedItemName

    @material.setter
    def material(self, value: 'str'):
        self.wrapped.Material.SetSelectedItem(str(value) if value else '')

    @property
    def pitch_cone_angle(self) -> 'float':
        '''float: 'PitchConeAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchConeAngle

    @property
    def addendum(self) -> 'float':
        '''float: 'Addendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Addendum

    @property
    def cutter_edge_radius(self) -> 'float':
        '''float: 'CutterEdgeRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterEdgeRadius

    @property
    def flank_roughness_rz(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FlankRoughnessRZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FlankRoughnessRZ) if self.wrapped.FlankRoughnessRZ is not None else None

    @flank_roughness_rz.setter
    def flank_roughness_rz(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FlankRoughnessRZ = value

    @property
    def relative_sensitivity_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RelativeSensitivityFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RelativeSensitivityFactor) if self.wrapped.RelativeSensitivityFactor is not None else None

    @relative_sensitivity_factor.setter
    def relative_sensitivity_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RelativeSensitivityFactor = value

    @property
    def tooth_form_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ToothFormFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ToothFormFactor) if self.wrapped.ToothFormFactor is not None else None

    @tooth_form_factor.setter
    def tooth_form_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ToothFormFactor = value

    @property
    def stress_correction_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'StressCorrectionFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.StressCorrectionFactor) if self.wrapped.StressCorrectionFactor is not None else None

    @stress_correction_factor.setter
    def stress_correction_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.StressCorrectionFactor = value

    @property
    def klingelnberg_cyclo_palloid_gear_material(self) -> '_561.KlingelnbergCycloPalloidConicalGearMaterial':
        '''KlingelnbergCycloPalloidConicalGearMaterial: 'KlingelnbergCycloPalloidGearMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_561.KlingelnbergCycloPalloidConicalGearMaterial)(self.wrapped.KlingelnbergCycloPalloidGearMaterial) if self.wrapped.KlingelnbergCycloPalloidGearMaterial is not None else None
