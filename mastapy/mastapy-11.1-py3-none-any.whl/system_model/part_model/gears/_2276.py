'''_2276.py

KlingelnbergCycloPalloidConicalGear
'''


from mastapy.system_model.part_model.gears import _2263
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidConicalGear')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGear',)


class KlingelnbergCycloPalloidConicalGear(_2263.ConicalGear):
    '''KlingelnbergCycloPalloidConicalGear

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
