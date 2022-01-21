'''_333.py

RateableMesh
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating', 'RateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('RateableMesh',)


class RateableMesh(_0.APIBase):
    '''RateableMesh

    This is a mastapy class.
    '''

    TYPE = _RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
