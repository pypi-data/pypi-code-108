'''_737.py

ConicalGearMicroGeometryConfig
'''


from mastapy.gears.manufacturing.bevel import _738
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MICRO_GEOMETRY_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalGearMicroGeometryConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMicroGeometryConfig',)


class ConicalGearMicroGeometryConfig(_738.ConicalGearMicroGeometryConfigBase):
    '''ConicalGearMicroGeometryConfig

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MICRO_GEOMETRY_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMicroGeometryConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
