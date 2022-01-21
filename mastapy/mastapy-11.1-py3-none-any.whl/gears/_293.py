'''_293.py

GearNurbSurface
'''


from mastapy.gears import _286
from mastapy._internal.python_net import python_net_import

_GEAR_NURB_SURFACE = python_net_import('SMT.MastaAPI.Gears', 'GearNurbSurface')


__docformat__ = 'restructuredtext en'
__all__ = ('GearNurbSurface',)


class GearNurbSurface(_286.ConicalGearToothSurface):
    '''GearNurbSurface

    This is a mastapy class.
    '''

    TYPE = _GEAR_NURB_SURFACE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearNurbSurface.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
