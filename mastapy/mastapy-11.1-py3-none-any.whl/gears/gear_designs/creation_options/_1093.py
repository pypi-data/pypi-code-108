'''_1093.py

CylindricalGearPairCreationOptions
'''


from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.gears.gear_designs.creation_options import _1094
from mastapy.gears.gear_designs.cylindrical import _984
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_PAIR_CREATION_OPTIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.CreationOptions', 'CylindricalGearPairCreationOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearPairCreationOptions',)


class CylindricalGearPairCreationOptions(_1094.GearSetCreationOptions['_984.CylindricalGearSetDesign']):
    '''CylindricalGearPairCreationOptions

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_PAIR_CREATION_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearPairCreationOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def derived_parameter(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CylindricalGearPairCreationOptions_DerivedParameterOption':
        '''enum_with_selected_value.EnumWithSelectedValue_CylindricalGearPairCreationOptions_DerivedParameterOption: 'DerivedParameter' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CylindricalGearPairCreationOptions_DerivedParameterOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DerivedParameter, value) if self.wrapped.DerivedParameter is not None else None

    @derived_parameter.setter
    def derived_parameter(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CylindricalGearPairCreationOptions_DerivedParameterOption.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CylindricalGearPairCreationOptions_DerivedParameterOption.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DerivedParameter = value

    @property
    def pinion_number_of_teeth(self) -> 'int':
        '''int: 'PinionNumberOfTeeth' is the original name of this property.'''

        return self.wrapped.PinionNumberOfTeeth

    @pinion_number_of_teeth.setter
    def pinion_number_of_teeth(self, value: 'int'):
        self.wrapped.PinionNumberOfTeeth = int(value) if value else 0

    @property
    def wheel_number_of_teeth(self) -> 'int':
        '''int: 'WheelNumberOfTeeth' is the original name of this property.'''

        return self.wrapped.WheelNumberOfTeeth

    @wheel_number_of_teeth.setter
    def wheel_number_of_teeth(self, value: 'int'):
        self.wrapped.WheelNumberOfTeeth = int(value) if value else 0

    @property
    def ratio_guide(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RatioGuide' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RatioGuide) if self.wrapped.RatioGuide is not None else None

    @ratio_guide.setter
    def ratio_guide(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RatioGuide = value

    @property
    def centre_distance(self) -> 'float':
        '''float: 'CentreDistance' is the original name of this property.'''

        return self.wrapped.CentreDistance

    @centre_distance.setter
    def centre_distance(self, value: 'float'):
        self.wrapped.CentreDistance = float(value) if value else 0.0

    @property
    def centre_distance_target(self) -> 'float':
        '''float: 'CentreDistanceTarget' is the original name of this property.'''

        return self.wrapped.CentreDistanceTarget

    @centre_distance_target.setter
    def centre_distance_target(self, value: 'float'):
        self.wrapped.CentreDistanceTarget = float(value) if value else 0.0

    @property
    def normal_module(self) -> 'float':
        '''float: 'NormalModule' is the original name of this property.'''

        return self.wrapped.NormalModule

    @normal_module.setter
    def normal_module(self, value: 'float'):
        self.wrapped.NormalModule = float(value) if value else 0.0

    @property
    def normal_module_target(self) -> 'float':
        '''float: 'NormalModuleTarget' is the original name of this property.'''

        return self.wrapped.NormalModuleTarget

    @normal_module_target.setter
    def normal_module_target(self, value: 'float'):
        self.wrapped.NormalModuleTarget = float(value) if value else 0.0

    @property
    def diametral_pitch(self) -> 'float':
        '''float: 'DiametralPitch' is the original name of this property.'''

        return self.wrapped.DiametralPitch

    @diametral_pitch.setter
    def diametral_pitch(self, value: 'float'):
        self.wrapped.DiametralPitch = float(value) if value else 0.0

    @property
    def diametral_pitch_target(self) -> 'float':
        '''float: 'DiametralPitchTarget' is the original name of this property.'''

        return self.wrapped.DiametralPitchTarget

    @diametral_pitch_target.setter
    def diametral_pitch_target(self, value: 'float'):
        self.wrapped.DiametralPitchTarget = float(value) if value else 0.0

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.'''

        return self.wrapped.HelixAngle

    @helix_angle.setter
    def helix_angle(self, value: 'float'):
        self.wrapped.HelixAngle = float(value) if value else 0.0

    @property
    def helix_angle_target(self) -> 'float':
        '''float: 'HelixAngleTarget' is the original name of this property.'''

        return self.wrapped.HelixAngleTarget

    @helix_angle_target.setter
    def helix_angle_target(self, value: 'float'):
        self.wrapped.HelixAngleTarget = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def pinion_face_width(self) -> 'float':
        '''float: 'PinionFaceWidth' is the original name of this property.'''

        return self.wrapped.PinionFaceWidth

    @pinion_face_width.setter
    def pinion_face_width(self, value: 'float'):
        self.wrapped.PinionFaceWidth = float(value) if value else 0.0

    @property
    def wheel_face_width(self) -> 'float':
        '''float: 'WheelFaceWidth' is the original name of this property.'''

        return self.wrapped.WheelFaceWidth

    @wheel_face_width.setter
    def wheel_face_width(self, value: 'float'):
        self.wrapped.WheelFaceWidth = float(value) if value else 0.0
