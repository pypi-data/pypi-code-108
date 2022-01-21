'''_2258.py

BevelDifferentialSunGear
'''


from mastapy.system_model.part_model.gears import _2255
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_SUN_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialSunGear')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialSunGear',)


class BevelDifferentialSunGear(_2255.BevelDifferentialGear):
    '''BevelDifferentialSunGear

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_SUN_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialSunGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
