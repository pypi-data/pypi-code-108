'''_2208.py

OuterBearingRaceMountingOptions
'''


from mastapy.system_model.part_model import _2183
from mastapy._internal.python_net import python_net_import

_OUTER_BEARING_RACE_MOUNTING_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'OuterBearingRaceMountingOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('OuterBearingRaceMountingOptions',)


class OuterBearingRaceMountingOptions(_2183.BearingRaceMountingOptions):
    '''OuterBearingRaceMountingOptions

    This is a mastapy class.
    '''

    TYPE = _OUTER_BEARING_RACE_MOUNTING_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OuterBearingRaceMountingOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
