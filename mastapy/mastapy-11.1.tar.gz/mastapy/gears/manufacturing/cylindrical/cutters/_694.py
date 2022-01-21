'''_694.py

CylindricalGearShaverDatabase
'''


from mastapy.gears.manufacturing.cylindrical import _570
from mastapy.gears.manufacturing.cylindrical.cutters import _693
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SHAVER_DATABASE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'CylindricalGearShaverDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearShaverDatabase',)


class CylindricalGearShaverDatabase(_570.CylindricalCutterDatabase['_693.CylindricalGearShaver']):
    '''CylindricalGearShaverDatabase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SHAVER_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearShaverDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
