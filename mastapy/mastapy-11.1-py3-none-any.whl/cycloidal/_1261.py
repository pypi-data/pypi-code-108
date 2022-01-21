'''_1261.py

RingPinsMaterial
'''


from mastapy.materials import _239
from mastapy._internal.python_net import python_net_import

_RING_PINS_MATERIAL = python_net_import('SMT.MastaAPI.Cycloidal', 'RingPinsMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsMaterial',)


class RingPinsMaterial(_239.Material):
    '''RingPinsMaterial

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
