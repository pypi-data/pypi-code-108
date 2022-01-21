'''_954.py

FaceGearWheelDesign
'''


from mastapy.gears.gear_designs.face import _947, _946
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_WHEEL_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Face', 'FaceGearWheelDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearWheelDesign',)


class FaceGearWheelDesign(_946.FaceGearDesign):
    '''FaceGearWheelDesign

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_WHEEL_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearWheelDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width_and_diameters_specification_method(self) -> '_947.FaceGearDiameterFaceWidthSpecificationMethod':
        '''FaceGearDiameterFaceWidthSpecificationMethod: 'FaceWidthAndDiametersSpecificationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FaceWidthAndDiametersSpecificationMethod)
        return constructor.new(_947.FaceGearDiameterFaceWidthSpecificationMethod)(value) if value is not None else None

    @face_width_and_diameters_specification_method.setter
    def face_width_and_diameters_specification_method(self, value: '_947.FaceGearDiameterFaceWidthSpecificationMethod'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FaceWidthAndDiametersSpecificationMethod = value

    @property
    def fillet_radius_at_reference_section(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FilletRadiusAtReferenceSection' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FilletRadiusAtReferenceSection) if self.wrapped.FilletRadiusAtReferenceSection is not None else None

    @fillet_radius_at_reference_section.setter
    def fillet_radius_at_reference_section(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FilletRadiusAtReferenceSection = value

    @property
    def rim_thickness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RimThickness' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RimThickness) if self.wrapped.RimThickness is not None else None

    @rim_thickness.setter
    def rim_thickness(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RimThickness = value

    @property
    def normal_thickness_at_reference_section(self) -> 'float':
        '''float: 'NormalThicknessAtReferenceSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThicknessAtReferenceSection

    @property
    def radius_at_inner_end(self) -> 'float':
        '''float: 'RadiusAtInnerEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusAtInnerEnd

    @property
    def radius_at_outer_end(self) -> 'float':
        '''float: 'RadiusAtOuterEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusAtOuterEnd

    @property
    def radius_at_mid_face(self) -> 'float':
        '''float: 'RadiusAtMidFace' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusAtMidFace

    @property
    def addendum_from_pitch_line_at_inner_end(self) -> 'float':
        '''float: 'AddendumFromPitchLineAtInnerEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumFromPitchLineAtInnerEnd

    @property
    def addendum_from_pitch_line_at_outer_end(self) -> 'float':
        '''float: 'AddendumFromPitchLineAtOuterEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumFromPitchLineAtOuterEnd

    @property
    def addendum_from_pitch_line_at_mid_face(self) -> 'float':
        '''float: 'AddendumFromPitchLineAtMidFace' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumFromPitchLineAtMidFace

    @property
    def dedendum_from_pitch_line_at_inner_end(self) -> 'float':
        '''float: 'DedendumFromPitchLineAtInnerEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DedendumFromPitchLineAtInnerEnd

    @property
    def dedendum_from_pitch_line_at_outer_end(self) -> 'float':
        '''float: 'DedendumFromPitchLineAtOuterEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DedendumFromPitchLineAtOuterEnd

    @property
    def dedendum_from_pitch_line_at_mid_face(self) -> 'float':
        '''float: 'DedendumFromPitchLineAtMidFace' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DedendumFromPitchLineAtMidFace

    @property
    def face_width_offset(self) -> 'float':
        '''float: 'FaceWidthOffset' is the original name of this property.'''

        return self.wrapped.FaceWidthOffset

    @face_width_offset.setter
    def face_width_offset(self, value: 'float'):
        self.wrapped.FaceWidthOffset = float(value) if value else 0.0

    @property
    def reference_pitch_radius(self) -> 'float':
        '''float: 'ReferencePitchRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferencePitchRadius

    @property
    def mean_diameter(self) -> 'float':
        '''float: 'MeanDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanDiameter

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

    @property
    def inner_diameter(self) -> 'float':
        '''float: 'InnerDiameter' is the original name of this property.'''

        return self.wrapped.InnerDiameter

    @inner_diameter.setter
    def inner_diameter(self, value: 'float'):
        self.wrapped.InnerDiameter = float(value) if value else 0.0

    @property
    def mean_pitch_diameter(self) -> 'float':
        '''float: 'MeanPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanPitchDiameter

    @property
    def mean_pitch_radius(self) -> 'float':
        '''float: 'MeanPitchRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanPitchRadius

    @property
    def profile_shift_coefficient(self) -> 'float':
        '''float: 'ProfileShiftCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileShiftCoefficient

    @property
    def normal_pressure_angle_at_inner_end(self) -> 'float':
        '''float: 'NormalPressureAngleAtInnerEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngleAtInnerEnd

    @property
    def normal_pressure_angle_at_outer_end(self) -> 'float':
        '''float: 'NormalPressureAngleAtOuterEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngleAtOuterEnd

    @property
    def normal_pressure_angle_at_mid_face(self) -> 'float':
        '''float: 'NormalPressureAngleAtMidFace' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngleAtMidFace

    @property
    def whole_depth(self) -> 'float':
        '''float: 'WholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WholeDepth

    @property
    def addendum(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Addendum' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Addendum) if self.wrapped.Addendum is not None else None

    @addendum.setter
    def addendum(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Addendum = value

    @property
    def dedendum(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Dedendum' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Dedendum) if self.wrapped.Dedendum is not None else None

    @dedendum.setter
    def dedendum(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Dedendum = value
