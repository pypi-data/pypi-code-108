'''_497.py

AGMA2101RateableMesh
'''


from mastapy.gears.rating.cylindrical import _433
from mastapy._internal.python_net import python_net_import

_AGMA2101_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.AGMA', 'AGMA2101RateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA2101RateableMesh',)


class AGMA2101RateableMesh(_433.CylindricalRateableMesh):
    '''AGMA2101RateableMesh

    This is a mastapy class.
    '''

    TYPE = _AGMA2101_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA2101RateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
