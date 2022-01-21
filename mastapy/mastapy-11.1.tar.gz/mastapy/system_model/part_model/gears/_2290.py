'''_2290.py

StraightBevelSunGear
'''


from mastapy.system_model.part_model.gears import _2285
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_SUN_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelSunGear')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelSunGear',)


class StraightBevelSunGear(_2285.StraightBevelDiffGear):
    '''StraightBevelSunGear

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_SUN_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelSunGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
