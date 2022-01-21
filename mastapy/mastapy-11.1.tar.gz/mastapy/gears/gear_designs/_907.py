'''_907.py

GearSetDesign
'''


from typing import List, Optional

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import
from mastapy.gears import _294
from mastapy.gears.fe_model import _1147
from mastapy.gears.fe_model.cylindrical import _1150
from mastapy._internal.cast_exception import CastException
from mastapy.gears.fe_model.conical import _1153
from mastapy.gears.gear_designs import _904, _905

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns', 'GearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetDesign',)


class GearSetDesign(_905.GearDesignComponent):
    '''GearSetDesign

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def long_name(self) -> 'str':
        '''str: 'LongName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LongName

    @property
    def fe_model(self) -> 'str':
        '''str: 'FEModel' is the original name of this property.'''

        return self.wrapped.FEModel.SelectedItemName

    @fe_model.setter
    def fe_model(self, value: 'str'):
        self.wrapped.FEModel.SetSelectedItem(str(value) if value else '')

    @property
    def gear_set_drawing(self) -> 'Image':
        '''Image: 'GearSetDrawing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.GearSetDrawing)
        return value

    @property
    def mass(self) -> 'float':
        '''float: 'Mass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Mass

    @property
    def name_including_tooth_numbers(self) -> 'str':
        '''str: 'NameIncludingToothNumbers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NameIncludingToothNumbers

    @property
    def required_safety_factor_for_contact(self) -> 'float':
        '''float: 'RequiredSafetyFactorForContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequiredSafetyFactorForContact

    @property
    def required_safety_factor_for_bending(self) -> 'float':
        '''float: 'RequiredSafetyFactorForBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequiredSafetyFactorForBending

    @property
    def required_safety_factor_for_static_contact(self) -> 'float':
        '''float: 'RequiredSafetyFactorForStaticContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequiredSafetyFactorForStaticContact

    @property
    def required_safety_factor_for_static_bending(self) -> 'float':
        '''float: 'RequiredSafetyFactorForStaticBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequiredSafetyFactorForStaticBending

    @property
    def largest_mesh_ratio(self) -> 'float':
        '''float: 'LargestMeshRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LargestMeshRatio

    @property
    def transverse_and_axial_contact_ratio_rating_for_nvh(self) -> 'float':
        '''float: 'TransverseAndAxialContactRatioRatingForNVH' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseAndAxialContactRatioRatingForNVH

    @property
    def transverse_contact_ratio_rating_for_nvh(self) -> 'float':
        '''float: 'TransverseContactRatioRatingForNVH' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatioRatingForNVH

    @property
    def axial_contact_ratio_rating_for_nvh(self) -> 'float':
        '''float: 'AxialContactRatioRatingForNVH' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialContactRatioRatingForNVH

    @property
    def smallest_number_of_teeth(self) -> 'int':
        '''int: 'SmallestNumberOfTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SmallestNumberOfTeeth

    @property
    def largest_number_of_teeth(self) -> 'int':
        '''int: 'LargestNumberOfTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LargestNumberOfTeeth

    @property
    def transmission_properties_gears(self) -> '_294.GearSetDesignGroup':
        '''GearSetDesignGroup: 'TransmissionPropertiesGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_294.GearSetDesignGroup)(self.wrapped.TransmissionPropertiesGears) if self.wrapped.TransmissionPropertiesGears is not None else None

    @property
    def active_ltcafe_model(self) -> '_1147.GearSetFEModel':
        '''GearSetFEModel: 'ActiveLTCAFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1147.GearSetFEModel.TYPE not in self.wrapped.ActiveLTCAFEModel.__class__.__mro__:
            raise CastException('Failed to cast active_ltcafe_model to GearSetFEModel. Expected: {}.'.format(self.wrapped.ActiveLTCAFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveLTCAFEModel.__class__)(self.wrapped.ActiveLTCAFEModel) if self.wrapped.ActiveLTCAFEModel is not None else None

    @property
    def active_ltcafe_model_of_type_cylindrical_gear_set_fe_model(self) -> '_1150.CylindricalGearSetFEModel':
        '''CylindricalGearSetFEModel: 'ActiveLTCAFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1150.CylindricalGearSetFEModel.TYPE not in self.wrapped.ActiveLTCAFEModel.__class__.__mro__:
            raise CastException('Failed to cast active_ltcafe_model to CylindricalGearSetFEModel. Expected: {}.'.format(self.wrapped.ActiveLTCAFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveLTCAFEModel.__class__)(self.wrapped.ActiveLTCAFEModel) if self.wrapped.ActiveLTCAFEModel is not None else None

    @property
    def active_ltcafe_model_of_type_conical_set_fe_model(self) -> '_1153.ConicalSetFEModel':
        '''ConicalSetFEModel: 'ActiveLTCAFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1153.ConicalSetFEModel.TYPE not in self.wrapped.ActiveLTCAFEModel.__class__.__mro__:
            raise CastException('Failed to cast active_ltcafe_model to ConicalSetFEModel. Expected: {}.'.format(self.wrapped.ActiveLTCAFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveLTCAFEModel.__class__)(self.wrapped.ActiveLTCAFEModel) if self.wrapped.ActiveLTCAFEModel is not None else None

    @property
    def tifffe_model(self) -> '_1147.GearSetFEModel':
        '''GearSetFEModel: 'TIFFFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1147.GearSetFEModel.TYPE not in self.wrapped.TIFFFEModel.__class__.__mro__:
            raise CastException('Failed to cast tifffe_model to GearSetFEModel. Expected: {}.'.format(self.wrapped.TIFFFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TIFFFEModel.__class__)(self.wrapped.TIFFFEModel) if self.wrapped.TIFFFEModel is not None else None

    @property
    def tifffe_model_of_type_cylindrical_gear_set_fe_model(self) -> '_1150.CylindricalGearSetFEModel':
        '''CylindricalGearSetFEModel: 'TIFFFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1150.CylindricalGearSetFEModel.TYPE not in self.wrapped.TIFFFEModel.__class__.__mro__:
            raise CastException('Failed to cast tifffe_model to CylindricalGearSetFEModel. Expected: {}.'.format(self.wrapped.TIFFFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TIFFFEModel.__class__)(self.wrapped.TIFFFEModel) if self.wrapped.TIFFFEModel is not None else None

    @property
    def tifffe_model_of_type_conical_set_fe_model(self) -> '_1153.ConicalSetFEModel':
        '''ConicalSetFEModel: 'TIFFFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1153.ConicalSetFEModel.TYPE not in self.wrapped.TIFFFEModel.__class__.__mro__:
            raise CastException('Failed to cast tifffe_model to ConicalSetFEModel. Expected: {}.'.format(self.wrapped.TIFFFEModel.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TIFFFEModel.__class__)(self.wrapped.TIFFFEModel) if self.wrapped.TIFFFEModel is not None else None

    @property
    def gears(self) -> 'List[_904.GearDesign]':
        '''List[GearDesign]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_904.GearDesign))
        return value

    @property
    def ltcafe_models(self) -> 'List[_1147.GearSetFEModel]':
        '''List[GearSetFEModel]: 'LTCAFEModels' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LTCAFEModels, constructor.new(_1147.GearSetFEModel))
        return value

    def create_new_fe_model(self):
        ''' 'CreateNewFEModel' is the original name of this method.'''

        self.wrapped.CreateNewFEModel()

    def create_new_tifffe_model(self):
        ''' 'CreateNewTIFFFEModel' is the original name of this method.'''

        self.wrapped.CreateNewTIFFFEModel()

    def copy(self, include_fe: Optional['bool'] = False) -> 'GearSetDesign':
        ''' 'Copy' is the original name of this method.

        Args:
            include_fe (bool, optional)

        Returns:
            mastapy.gears.gear_designs.GearSetDesign
        '''

        include_fe = bool(include_fe)
        method_result = self.wrapped.Copy(include_fe if include_fe else False)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
