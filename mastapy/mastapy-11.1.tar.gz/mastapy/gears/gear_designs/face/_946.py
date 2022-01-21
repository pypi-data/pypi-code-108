'''_946.py

FaceGearDesign
'''


from mastapy.gears import _299
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.python_net import python_net_import
from mastapy.gears.gear_designs import _904

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_FACE_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Face', 'FaceGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearDesign',)


class FaceGearDesign(_904.GearDesign):
    '''FaceGearDesign

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearDesign.TYPE'):
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
        '''float: 'WorkingPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingPitchDiameter

    @property
    def working_pitch_radius(self) -> 'float':
        '''float: 'WorkingPitchRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WorkingPitchRadius

    @property
    def reference_diameter(self) -> 'float':
        '''float: 'ReferenceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceDiameter

    @property
    def pitch_angle(self) -> 'float':
        '''float: 'PitchAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchAngle

    @property
    def mean_point_to_crossing_point(self) -> 'float':
        '''float: 'MeanPointToCrossingPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanPointToCrossingPoint

    @property
    def iso_material(self) -> 'str':
        '''str: 'ISOMaterial' is the original name of this property.'''

        return self.wrapped.ISOMaterial.SelectedItemName

    @iso_material.setter
    def iso_material(self, value: 'str'):
        self.wrapped.ISOMaterial.SetSelectedItem(str(value) if value else '')
