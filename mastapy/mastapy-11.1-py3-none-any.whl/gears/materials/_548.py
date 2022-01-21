'''_548.py

BevelGearMaterialDatabase
'''


from mastapy.gears.materials import _555, _547
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MATERIAL_DATABASE = python_net_import('SMT.MastaAPI.Gears.Materials', 'BevelGearMaterialDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMaterialDatabase',)


class BevelGearMaterialDatabase(_555.GearMaterialDatabase['_547.BevelGearMaterial']):
    '''BevelGearMaterialDatabase

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MATERIAL_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMaterialDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
