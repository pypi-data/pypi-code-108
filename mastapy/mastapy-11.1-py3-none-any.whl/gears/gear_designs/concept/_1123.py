'''_1123.py

ConceptGearDesign
'''


from mastapy.gears import _299
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears.gear_designs import _904
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Concept', 'ConceptGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearDesign',)


class ConceptGearDesign(_904.GearDesign):
    '''ConceptGearDesign

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hand(self) -> '_299.Hand':
        '''Hand: 'Hand' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Hand)
        return constructor.new(_299.Hand)(value) if value is not None else None

    @hand.setter
    def hand(self, value: '_299.Hand'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Hand = value

    @property
    def working_pitch_diameter(self) -> 'float':
        '''float: 'WorkingPitchDiameter' is the original name of this property.'''

        return self.wrapped.WorkingPitchDiameter

    @working_pitch_diameter.setter
    def working_pitch_diameter(self, value: 'float'):
        self.wrapped.WorkingPitchDiameter = float(value) if value else 0.0

    @property
    def pitch_angle(self) -> 'float':
        '''float: 'PitchAngle' is the original name of this property.'''

        return self.wrapped.PitchAngle

    @pitch_angle.setter
    def pitch_angle(self, value: 'float'):
        self.wrapped.PitchAngle = float(value) if value else 0.0

    @property
    def working_helix_angle(self) -> 'float':
        '''float: 'WorkingHelixAngle' is the original name of this property.'''

        return self.wrapped.WorkingHelixAngle

    @working_helix_angle.setter
    def working_helix_angle(self, value: 'float'):
        self.wrapped.WorkingHelixAngle = float(value) if value else 0.0

    @property
    def mean_point_to_crossing_point(self) -> 'float':
        '''float: 'MeanPointToCrossingPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanPointToCrossingPoint

    @property
    def pitch_apex_to_crossing_point(self) -> 'float':
        '''float: 'PitchApexToCrossingPoint' is the original name of this property.'''

        return self.wrapped.PitchApexToCrossingPoint

    @pitch_apex_to_crossing_point.setter
    def pitch_apex_to_crossing_point(self, value: 'float'):
        self.wrapped.PitchApexToCrossingPoint = float(value) if value else 0.0
