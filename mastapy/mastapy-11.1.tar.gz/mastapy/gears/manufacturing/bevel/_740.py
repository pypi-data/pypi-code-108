'''_740.py

ConicalMeshedWheelFlankManufacturingConfig
'''


from mastapy.gears import _286
from mastapy._internal.python_net import python_net_import

_CONICAL_MESHED_WHEEL_FLANK_MANUFACTURING_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalMeshedWheelFlankManufacturingConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshedWheelFlankManufacturingConfig',)


class ConicalMeshedWheelFlankManufacturingConfig(_286.ConicalGearToothSurface):
    '''ConicalMeshedWheelFlankManufacturingConfig

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESHED_WHEEL_FLANK_MANUFACTURING_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshedWheelFlankManufacturingConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
