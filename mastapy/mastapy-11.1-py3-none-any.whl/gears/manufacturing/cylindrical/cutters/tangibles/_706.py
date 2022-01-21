'''_706.py

CylindricalGearWormGrinderShape
'''


from mastapy.gears.manufacturing.cylindrical.cutters.tangibles import _708
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_WORM_GRINDER_SHAPE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters.Tangibles', 'CylindricalGearWormGrinderShape')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearWormGrinderShape',)


class CylindricalGearWormGrinderShape(_708.RackShape):
    '''CylindricalGearWormGrinderShape

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_WORM_GRINDER_SHAPE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearWormGrinderShape.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
