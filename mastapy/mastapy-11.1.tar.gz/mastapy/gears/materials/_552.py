'''_552.py

CylindricalGearMaterialDatabase
'''


from typing import Generic, TypeVar

from mastapy.materials import _240
from mastapy.gears.materials import _551
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MATERIAL_DATABASE = python_net_import('SMT.MastaAPI.Gears.Materials', 'CylindricalGearMaterialDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMaterialDatabase',)


T = TypeVar('T', bound='_551.CylindricalGearMaterial')


class CylindricalGearMaterialDatabase(_240.MaterialDatabase['T'], Generic[T]):
    '''CylindricalGearMaterialDatabase

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _CYLINDRICAL_GEAR_MATERIAL_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMaterialDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
