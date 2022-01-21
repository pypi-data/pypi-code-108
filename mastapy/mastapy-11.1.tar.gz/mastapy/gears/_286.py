'''_286.py

ConicalGearToothSurface
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_TOOTH_SURFACE = python_net_import('SMT.MastaAPI.Gears', 'ConicalGearToothSurface')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearToothSurface',)


class ConicalGearToothSurface(_0.APIBase):
    '''ConicalGearToothSurface

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_TOOTH_SURFACE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearToothSurface.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
