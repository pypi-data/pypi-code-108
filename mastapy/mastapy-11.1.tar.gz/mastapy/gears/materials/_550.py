'''_550.py

CylindricalGearISOMaterialDatabase
'''


from mastapy.gears.materials import _552, _557
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_ISO_MATERIAL_DATABASE = python_net_import('SMT.MastaAPI.Gears.Materials', 'CylindricalGearISOMaterialDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearISOMaterialDatabase',)


class CylindricalGearISOMaterialDatabase(_552.CylindricalGearMaterialDatabase['_557.ISOCylindricalGearMaterial']):
    '''CylindricalGearISOMaterialDatabase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_ISO_MATERIAL_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearISOMaterialDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
