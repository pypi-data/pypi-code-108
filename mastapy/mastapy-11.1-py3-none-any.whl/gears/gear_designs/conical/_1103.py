'''_1103.py

ConicalGearSetDesign
'''


from typing import List

from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.conical import _1102
from mastapy.gears.gear_designs import _907
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'ConicalGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetDesign',)


class ConicalGearSetDesign(_907.GearSetDesign):
    '''ConicalGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def dominant_pinion(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'DominantPinion' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.DominantPinion) if self.wrapped.DominantPinion is not None else None

    @dominant_pinion.setter
    def dominant_pinion(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.DominantPinion = value

    @property
    def imported_xml_file_name(self) -> 'str':
        '''str: 'ImportedXMLFileName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ImportedXMLFileName

    @property
    def module(self) -> 'float':
        '''float: 'Module' is the original name of this property.'''

        return self.wrapped.Module

    @module.setter
    def module(self, value: 'float'):
        self.wrapped.Module = float(value) if value else 0.0

    @property
    def circular_pitch(self) -> 'float':
        '''float: 'CircularPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CircularPitch

    @property
    def wheel_pitch_diameter(self) -> 'float':
        '''float: 'WheelPitchDiameter' is the original name of this property.'''

        return self.wrapped.WheelPitchDiameter

    @wheel_pitch_diameter.setter
    def wheel_pitch_diameter(self, value: 'float'):
        self.wrapped.WheelPitchDiameter = float(value) if value else 0.0

    @property
    def wheel_outer_cone_distance(self) -> 'float':
        '''float: 'WheelOuterConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelOuterConeDistance

    @property
    def wheel_mean_cone_distance(self) -> 'float':
        '''float: 'WheelMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelMeanConeDistance

    @property
    def wheel_finish_cutter_point_width(self) -> 'float':
        '''float: 'WheelFinishCutterPointWidth' is the original name of this property.'''

        return self.wrapped.WheelFinishCutterPointWidth

    @wheel_finish_cutter_point_width.setter
    def wheel_finish_cutter_point_width(self, value: 'float'):
        self.wrapped.WheelFinishCutterPointWidth = float(value) if value else 0.0

    @property
    def mean_normal_module(self) -> 'float':
        '''float: 'MeanNormalModule' is the original name of this property.'''

        return self.wrapped.MeanNormalModule

    @mean_normal_module.setter
    def mean_normal_module(self, value: 'float'):
        self.wrapped.MeanNormalModule = float(value) if value else 0.0

    @property
    def cutter_radius(self) -> 'float':
        '''float: 'CutterRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterRadius

    @property
    def conical_meshes(self) -> 'List[_1102.ConicalGearMeshDesign]':
        '''List[ConicalGearMeshDesign]: 'ConicalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConicalMeshes, constructor.new(_1102.ConicalGearMeshDesign))
        return value
