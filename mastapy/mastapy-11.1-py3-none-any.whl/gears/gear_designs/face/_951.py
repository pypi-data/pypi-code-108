'''_951.py

FaceGearPinionDesign
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.face import _946
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_PINION_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Face', 'FaceGearPinionDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearPinionDesign',)


class FaceGearPinionDesign(_946.FaceGearDesign):
    '''FaceGearPinionDesign

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_PINION_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearPinionDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pitch_cone_angle_with_gear(self) -> 'float':
        '''float: 'PitchConeAngleWithGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchConeAngleWithGear

    @property
    def base_diameter(self) -> 'float':
        '''float: 'BaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameter

    @property
    def base_thickness_half_angle(self) -> 'float':
        '''float: 'BaseThicknessHalfAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseThicknessHalfAngle

    @property
    def normal_thickness(self) -> 'float':
        '''float: 'NormalThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThickness

    @property
    def tip_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TipDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TipDiameter) if self.wrapped.TipDiameter is not None else None

    @tip_diameter.setter
    def tip_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TipDiameter = value

    @property
    def root_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RootDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RootDiameter) if self.wrapped.RootDiameter is not None else None

    @root_diameter.setter
    def root_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RootDiameter = value

    @property
    def fillet_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FilletRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FilletRadius) if self.wrapped.FilletRadius is not None else None

    @fillet_radius.setter
    def fillet_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FilletRadius = value

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidth

    @property
    def profile_shift_coefficient(self) -> 'float':
        '''float: 'ProfileShiftCoefficient' is the original name of this property.'''

        return self.wrapped.ProfileShiftCoefficient

    @profile_shift_coefficient.setter
    def profile_shift_coefficient(self, value: 'float'):
        self.wrapped.ProfileShiftCoefficient = float(value) if value else 0.0

    @property
    def whole_depth(self) -> 'float':
        '''float: 'WholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WholeDepth
