'''_2136.py

GearMeshingOptions
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.gears.fe_model import _1146
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_MESHING_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'GearMeshingOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshingOptions',)


class GearMeshingOptions(_0.APIBase):
    '''GearMeshingOptions

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESHING_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshingOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Diameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Diameter) if self.wrapped.Diameter is not None else None

    @diameter.setter
    def diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Diameter = value

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def mesh_teeth(self) -> 'bool':
        '''bool: 'MeshTeeth' is the original name of this property.'''

        return self.wrapped.MeshTeeth

    @mesh_teeth.setter
    def mesh_teeth(self, value: 'bool'):
        self.wrapped.MeshTeeth = bool(value) if value else False

    @property
    def offset_of_gear_centre_calculated_from_fe(self) -> 'str':
        '''str: 'OffsetOfGearCentreCalculatedFromFE' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OffsetOfGearCentreCalculatedFromFE

    @property
    def element_settings(self) -> '_1146.GearMeshingElementOptions':
        '''GearMeshingElementOptions: 'ElementSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1146.GearMeshingElementOptions)(self.wrapped.ElementSettings) if self.wrapped.ElementSettings is not None else None
