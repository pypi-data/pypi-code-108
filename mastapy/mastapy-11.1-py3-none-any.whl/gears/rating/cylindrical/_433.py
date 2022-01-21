'''_433.py

CylindricalRateableMesh
'''


from mastapy.gears.rating import _333
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'CylindricalRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalRateableMesh',)


class CylindricalRateableMesh(_333.RateableMesh):
    '''CylindricalRateableMesh

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
