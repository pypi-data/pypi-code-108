'''_1266.py

BoltGeometry
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.bolts import (
    _1282, _1270, _1271, _1277,
    _1284, _1272
)
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_BOLT_GEOMETRY = python_net_import('SMT.MastaAPI.Bolts', 'BoltGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltGeometry',)


class BoltGeometry(_1597.NamedDatabaseItem):
    '''BoltGeometry

    This is a mastapy class.
    '''

    TYPE = _BOLT_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bolt_name(self) -> 'str':
        '''str: 'BoltName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BoltName

    @property
    def width_across_flats(self) -> 'float':
        '''float: 'WidthAcrossFlats' is the original name of this property.'''

        return self.wrapped.WidthAcrossFlats

    @width_across_flats.setter
    def width_across_flats(self, value: 'float'):
        self.wrapped.WidthAcrossFlats = float(value) if value else 0.0

    @property
    def bolt_thread_pitch_diameter(self) -> 'float':
        '''float: 'BoltThreadPitchDiameter' is the original name of this property.'''

        return self.wrapped.BoltThreadPitchDiameter

    @bolt_thread_pitch_diameter.setter
    def bolt_thread_pitch_diameter(self, value: 'float'):
        self.wrapped.BoltThreadPitchDiameter = float(value) if value else 0.0

    @property
    def pitch_of_thread(self) -> 'float':
        '''float: 'PitchOfThread' is the original name of this property.'''

        return self.wrapped.PitchOfThread

    @pitch_of_thread.setter
    def pitch_of_thread(self, value: 'float'):
        self.wrapped.PitchOfThread = float(value) if value else 0.0

    @property
    def bolt_length(self) -> 'float':
        '''float: 'BoltLength' is the original name of this property.'''

        return self.wrapped.BoltLength

    @bolt_length.setter
    def bolt_length(self, value: 'float'):
        self.wrapped.BoltLength = float(value) if value else 0.0

    @property
    def outside_diameter_of_clamped_parts(self) -> 'float':
        '''float: 'OutsideDiameterOfClampedParts' is the original name of this property.'''

        return self.wrapped.OutsideDiameterOfClampedParts

    @outside_diameter_of_clamped_parts.setter
    def outside_diameter_of_clamped_parts(self, value: 'float'):
        self.wrapped.OutsideDiameterOfClampedParts = float(value) if value else 0.0

    @property
    def minor_diameter_of_bolt_thread(self) -> 'float':
        '''float: 'MinorDiameterOfBoltThread' is the original name of this property.'''

        return self.wrapped.MinorDiameterOfBoltThread

    @minor_diameter_of_bolt_thread.setter
    def minor_diameter_of_bolt_thread(self, value: 'float'):
        self.wrapped.MinorDiameterOfBoltThread = float(value) if value else 0.0

    @property
    def bolt_diameter(self) -> 'float':
        '''float: 'BoltDiameter' is the original name of this property.'''

        return self.wrapped.BoltDiameter

    @bolt_diameter.setter
    def bolt_diameter(self, value: 'float'):
        self.wrapped.BoltDiameter = float(value) if value else 0.0

    @property
    def bolt_inner_diameter(self) -> 'float':
        '''float: 'BoltInnerDiameter' is the original name of this property.'''

        return self.wrapped.BoltInnerDiameter

    @bolt_inner_diameter.setter
    def bolt_inner_diameter(self, value: 'float'):
        self.wrapped.BoltInnerDiameter = float(value) if value else 0.0

    @property
    def nut_thread_minor_diameter(self) -> 'float':
        '''float: 'NutThreadMinorDiameter' is the original name of this property.'''

        return self.wrapped.NutThreadMinorDiameter

    @nut_thread_minor_diameter.setter
    def nut_thread_minor_diameter(self, value: 'float'):
        self.wrapped.NutThreadMinorDiameter = float(value) if value else 0.0

    @property
    def tapped_thread_minor_diameter(self) -> 'float':
        '''float: 'TappedThreadMinorDiameter' is the original name of this property.'''

        return self.wrapped.TappedThreadMinorDiameter

    @tapped_thread_minor_diameter.setter
    def tapped_thread_minor_diameter(self, value: 'float'):
        self.wrapped.TappedThreadMinorDiameter = float(value) if value else 0.0

    @property
    def nut_thread_pitch_diameter(self) -> 'float':
        '''float: 'NutThreadPitchDiameter' is the original name of this property.'''

        return self.wrapped.NutThreadPitchDiameter

    @nut_thread_pitch_diameter.setter
    def nut_thread_pitch_diameter(self, value: 'float'):
        self.wrapped.NutThreadPitchDiameter = float(value) if value else 0.0

    @property
    def tapped_thread_pitch_diameter(self) -> 'float':
        '''float: 'TappedThreadPitchDiameter' is the original name of this property.'''

        return self.wrapped.TappedThreadPitchDiameter

    @tapped_thread_pitch_diameter.setter
    def tapped_thread_pitch_diameter(self, value: 'float'):
        self.wrapped.TappedThreadPitchDiameter = float(value) if value else 0.0

    @property
    def standard_size(self) -> '_1282.StandardSizes':
        '''StandardSizes: 'StandardSize' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.StandardSize)
        return constructor.new(_1282.StandardSizes)(value) if value is not None else None

    @standard_size.setter
    def standard_size(self, value: '_1282.StandardSizes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.StandardSize = value

    @property
    def bolt_sections(self) -> 'List[_1270.BoltSection]':
        '''List[BoltSection]: 'BoltSections' is the original name of this property.'''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoltSections, constructor.new(_1270.BoltSection))
        return value

    @bolt_sections.setter
    def bolt_sections(self, value: 'List[_1270.BoltSection]'):
        value = value if value else None
        value = conversion.mp_to_pn_objects_in_list(value)
        self.wrapped.BoltSections = value

    @property
    def has_cross_sections_of_different_diameters(self) -> 'bool':
        '''bool: 'HasCrossSectionsOfDifferentDiameters' is the original name of this property.'''

        return self.wrapped.HasCrossSectionsOfDifferentDiameters

    @has_cross_sections_of_different_diameters.setter
    def has_cross_sections_of_different_diameters(self, value: 'bool'):
        self.wrapped.HasCrossSectionsOfDifferentDiameters = bool(value) if value else False

    @property
    def shank_length(self) -> 'float':
        '''float: 'ShankLength' is the original name of this property.'''

        return self.wrapped.ShankLength

    @shank_length.setter
    def shank_length(self, value: 'float'):
        self.wrapped.ShankLength = float(value) if value else 0.0

    @property
    def shank_diameter(self) -> 'float':
        '''float: 'ShankDiameter' is the original name of this property.'''

        return self.wrapped.ShankDiameter

    @shank_diameter.setter
    def shank_diameter(self, value: 'float'):
        self.wrapped.ShankDiameter = float(value) if value else 0.0

    @property
    def shank_inner_diameter(self) -> 'float':
        '''float: 'ShankInnerDiameter' is the original name of this property.'''

        return self.wrapped.ShankInnerDiameter

    @shank_inner_diameter.setter
    def shank_inner_diameter(self, value: 'float'):
        self.wrapped.ShankInnerDiameter = float(value) if value else 0.0

    @property
    def bolt_shank_type(self) -> '_1271.BoltShankType':
        '''BoltShankType: 'BoltShankType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.BoltShankType)
        return constructor.new(_1271.BoltShankType)(value) if value is not None else None

    @bolt_shank_type.setter
    def bolt_shank_type(self, value: '_1271.BoltShankType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.BoltShankType = value

    @property
    def hole_diameter_of_clamped_parts(self) -> 'float':
        '''float: 'HoleDiameterOfClampedParts' is the original name of this property.'''

        return self.wrapped.HoleDiameterOfClampedParts

    @hole_diameter_of_clamped_parts.setter
    def hole_diameter_of_clamped_parts(self, value: 'float'):
        self.wrapped.HoleDiameterOfClampedParts = float(value) if value else 0.0

    @property
    def type_of_head_cap(self) -> '_1277.HeadCapTypes':
        '''HeadCapTypes: 'TypeOfHeadCap' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TypeOfHeadCap)
        return constructor.new(_1277.HeadCapTypes)(value) if value is not None else None

    @type_of_head_cap.setter
    def type_of_head_cap(self, value: '_1277.HeadCapTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TypeOfHeadCap = value

    @property
    def type_of_thread(self) -> '_1284.ThreadTypes':
        '''ThreadTypes: 'TypeOfThread' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TypeOfThread)
        return constructor.new(_1284.ThreadTypes)(value) if value is not None else None

    @type_of_thread.setter
    def type_of_thread(self, value: '_1284.ThreadTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TypeOfThread = value

    @property
    def is_threaded_to_head(self) -> 'bool':
        '''bool: 'IsThreadedToHead' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsThreadedToHead

    @property
    def type_of_bolted_joint(self) -> '_1272.BoltTypes':
        '''BoltTypes: 'TypeOfBoltedJoint' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TypeOfBoltedJoint)
        return constructor.new(_1272.BoltTypes)(value) if value is not None else None

    @type_of_bolted_joint.setter
    def type_of_bolted_joint(self, value: '_1272.BoltTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TypeOfBoltedJoint = value

    @property
    def hole_chamfer_width(self) -> 'float':
        '''float: 'HoleChamferWidth' is the original name of this property.'''

        return self.wrapped.HoleChamferWidth

    @hole_chamfer_width.setter
    def hole_chamfer_width(self, value: 'float'):
        self.wrapped.HoleChamferWidth = float(value) if value else 0.0
