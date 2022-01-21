'''_2260.py

BevelGearSet
'''


from mastapy.system_model.part_model.gears import _2254
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelGearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSet',)


class BevelGearSet(_2254.AGMAGleasonConicalGearSet):
    '''BevelGearSet

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
