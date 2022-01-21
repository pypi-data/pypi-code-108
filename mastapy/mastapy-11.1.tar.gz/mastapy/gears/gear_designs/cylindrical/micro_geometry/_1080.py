'''_1080.py

TotalProfileReliefWithDeviation
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1075
from mastapy._internal.python_net import python_net_import

_TOTAL_PROFILE_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'TotalProfileReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('TotalProfileReliefWithDeviation',)


class TotalProfileReliefWithDeviation(_1075.ProfileReliefWithDeviation):
    '''TotalProfileReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _TOTAL_PROFILE_RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TotalProfileReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
