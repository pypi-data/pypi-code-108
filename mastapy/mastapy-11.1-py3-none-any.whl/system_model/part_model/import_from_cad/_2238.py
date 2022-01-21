'''_2238.py

CylindricalGearFromCAD
'''


from mastapy._internal.implicit import list_with_selected_item, overridable
from mastapy.system_model.part_model.gears import _2266, _2265
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.geometry.two_d import _278
from mastapy.system_model.part_model.import_from_cad import _2244
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'CylindricalGearFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFromCAD',)


class CylindricalGearFromCAD(_2244.MountableComponentFromCAD):
    '''CylindricalGearFromCAD

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def existing_gear_set(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalGearSet':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalGearSet: 'ExistingGearSet' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalGearSet)(self.wrapped.ExistingGearSet) if self.wrapped.ExistingGearSet is not None else None

    @existing_gear_set.setter
    def existing_gear_set(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalGearSet.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearSet.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalGearSet.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.ExistingGearSet = value

    @property
    def meshing_gear(self) -> 'list_with_selected_item.ListWithSelectedItem_CylindricalGear':
        '''list_with_selected_item.ListWithSelectedItem_CylindricalGear: 'MeshingGear' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_CylindricalGear)(self.wrapped.MeshingGear) if self.wrapped.MeshingGear is not None else None

    @meshing_gear.setter
    def meshing_gear(self, value: 'list_with_selected_item.ListWithSelectedItem_CylindricalGear.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_CylindricalGear.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_CylindricalGear.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.MeshingGear = value

    @property
    def number_of_teeth(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'NumberOfTeeth' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.NumberOfTeeth) if self.wrapped.NumberOfTeeth is not None else None

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.NumberOfTeeth = value

    @property
    def gear_set_name(self) -> 'str':
        '''str: 'GearSetName' is the original name of this property.'''

        return self.wrapped.GearSetName

    @gear_set_name.setter
    def gear_set_name(self, value: 'str'):
        self.wrapped.GearSetName = str(value) if value else ''

    @property
    def internal_external(self) -> '_278.InternalExternalType':
        '''InternalExternalType: 'InternalExternal' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.InternalExternal)
        return constructor.new(_278.InternalExternalType)(value) if value is not None else None

    @internal_external.setter
    def internal_external(self, value: '_278.InternalExternalType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.InternalExternal = value

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def centre_distance(self) -> 'float':
        '''float: 'CentreDistance' is the original name of this property.'''

        return self.wrapped.CentreDistance

    @centre_distance.setter
    def centre_distance(self, value: 'float'):
        self.wrapped.CentreDistance = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.'''

        return self.wrapped.HelixAngle

    @helix_angle.setter
    def helix_angle(self, value: 'float'):
        self.wrapped.HelixAngle = float(value) if value else 0.0

    @property
    def normal_module(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'NormalModule' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.NormalModule) if self.wrapped.NormalModule is not None else None

    @normal_module.setter
    def normal_module(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.NormalModule = value

    @property
    def tip_diameter(self) -> 'float':
        '''float: 'TipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipDiameter

    @property
    def root_diameter(self) -> 'float':
        '''float: 'RootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootDiameter

    @property
    def cad_drawing_diameter(self) -> 'float':
        '''float: 'CADDrawingDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CADDrawingDiameter
