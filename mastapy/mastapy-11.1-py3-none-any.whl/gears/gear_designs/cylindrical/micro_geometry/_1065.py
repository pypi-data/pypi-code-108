'''_1065.py

LeadSlopeReliefWithDeviation
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1064
from mastapy._internal.python_net import python_net_import

_LEAD_SLOPE_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'LeadSlopeReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('LeadSlopeReliefWithDeviation',)


class LeadSlopeReliefWithDeviation(_1064.LeadReliefWithDeviation):
    '''LeadSlopeReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _LEAD_SLOPE_RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LeadSlopeReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
