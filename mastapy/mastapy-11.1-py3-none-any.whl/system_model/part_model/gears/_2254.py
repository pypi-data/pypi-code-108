'''_2254.py

AGMAGleasonConicalGearSet
'''


from mastapy.system_model.part_model.gears import _2264
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_SET = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'AGMAGleasonConicalGearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearSet',)


class AGMAGleasonConicalGearSet(_2264.ConicalGearSet):
    '''AGMAGleasonConicalGearSet

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
