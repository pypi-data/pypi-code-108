'''_585.py

CylindricalSetManufacturingConfig
'''


from typing import List

from mastapy.gears.manufacturing.cylindrical import _582, _572
from mastapy._internal import constructor, conversion
from mastapy.gears.analysis import _1175
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_SET_MANUFACTURING_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'CylindricalSetManufacturingConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalSetManufacturingConfig',)


class CylindricalSetManufacturingConfig(_1175.GearSetImplementationDetail):
    '''CylindricalSetManufacturingConfig

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_SET_MANUFACTURING_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalSetManufacturingConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cylindrical_mesh_manufacturing_configurations(self) -> 'List[_582.CylindricalMeshManufacturingConfig]':
        '''List[CylindricalMeshManufacturingConfig]: 'CylindricalMeshManufacturingConfigurations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshManufacturingConfigurations, constructor.new(_582.CylindricalMeshManufacturingConfig))
        return value

    @property
    def cylindrical_gear_manufacturing_configurations(self) -> 'List[_572.CylindricalGearManufacturingConfig]':
        '''List[CylindricalGearManufacturingConfig]: 'CylindricalGearManufacturingConfigurations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearManufacturingConfigurations, constructor.new(_572.CylindricalGearManufacturingConfig))
        return value
