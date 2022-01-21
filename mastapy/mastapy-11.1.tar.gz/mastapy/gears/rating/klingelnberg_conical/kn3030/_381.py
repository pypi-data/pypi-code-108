'''_381.py

KlingelnbergConicalRateableMesh
'''


from mastapy.gears.rating import _333
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CONICAL_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.KlingelnbergConical.KN3030', 'KlingelnbergConicalRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergConicalRateableMesh',)


class KlingelnbergConicalRateableMesh(_333.RateableMesh):
    '''KlingelnbergConicalRateableMesh

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CONICAL_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergConicalRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
