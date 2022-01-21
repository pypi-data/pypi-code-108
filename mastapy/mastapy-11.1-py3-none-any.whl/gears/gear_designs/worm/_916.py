'''_916.py

WormGearSetDesign
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _317
from mastapy.gears.gear_designs.worm import _914, _915
from mastapy.gears.gear_designs import _907
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Worm', 'WormGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearSetDesign',)


class WormGearSetDesign(_907.GearSetDesign):
    '''WormGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial_module(self) -> 'float':
        '''float: 'AxialModule' is the original name of this property.'''

        return self.wrapped.AxialModule

    @axial_module.setter
    def axial_module(self, value: 'float'):
        self.wrapped.AxialModule = float(value) if value else 0.0

    @property
    def worm_type(self) -> '_317.WormType':
        '''WormType: 'WormType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.WormType)
        return constructor.new(_317.WormType)(value) if value is not None else None

    @worm_type.setter
    def worm_type(self, value: '_317.WormType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.WormType = value

    @property
    def axial_pressure_angle(self) -> 'float':
        '''float: 'AxialPressureAngle' is the original name of this property.'''

        return self.wrapped.AxialPressureAngle

    @axial_pressure_angle.setter
    def axial_pressure_angle(self, value: 'float'):
        self.wrapped.AxialPressureAngle = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def gears(self) -> 'List[_914.WormGearDesign]':
        '''List[WormGearDesign]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_914.WormGearDesign))
        return value

    @property
    def worm_gears(self) -> 'List[_914.WormGearDesign]':
        '''List[WormGearDesign]: 'WormGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormGears, constructor.new(_914.WormGearDesign))
        return value

    @property
    def worm_meshes(self) -> 'List[_915.WormGearMeshDesign]':
        '''List[WormGearMeshDesign]: 'WormMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.WormMeshes, constructor.new(_915.WormGearMeshDesign))
        return value
