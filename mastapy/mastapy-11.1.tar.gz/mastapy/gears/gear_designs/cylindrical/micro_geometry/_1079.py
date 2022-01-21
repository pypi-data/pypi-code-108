'''_1079.py

TotalLeadReliefWithDeviation
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1064
from mastapy._internal.python_net import python_net_import

_TOTAL_LEAD_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'TotalLeadReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('TotalLeadReliefWithDeviation',)


class TotalLeadReliefWithDeviation(_1064.LeadReliefWithDeviation):
    '''TotalLeadReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _TOTAL_LEAD_RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TotalLeadReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
