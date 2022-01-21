'''_1063.py

LeadFormReliefWithDeviation
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1064
from mastapy._internal.python_net import python_net_import

_LEAD_FORM_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'LeadFormReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('LeadFormReliefWithDeviation',)


class LeadFormReliefWithDeviation(_1064.LeadReliefWithDeviation):
    '''LeadFormReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _LEAD_FORM_RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LeadFormReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
