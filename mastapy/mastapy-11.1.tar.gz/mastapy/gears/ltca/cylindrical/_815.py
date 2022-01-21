'''_815.py

CylindricalGearFESettings
'''


from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FE_SETTINGS = python_net_import('SMT.MastaAPI.Gears.LTCA.Cylindrical', 'CylindricalGearFESettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFESettings',)


class CylindricalGearFESettings(_1387.PerMachineSettings):
    '''CylindricalGearFESettings

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFESettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
