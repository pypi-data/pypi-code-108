'''_1064.py

LeadReliefWithDeviation
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1077
from mastapy._internal.python_net import python_net_import

_LEAD_RELIEF_WITH_DEVIATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'LeadReliefWithDeviation')


__docformat__ = 'restructuredtext en'
__all__ = ('LeadReliefWithDeviation',)


class LeadReliefWithDeviation(_1077.ReliefWithDeviation):
    '''LeadReliefWithDeviation

    This is a mastapy class.
    '''

    TYPE = _LEAD_RELIEF_WITH_DEVIATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LeadReliefWithDeviation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def distance_along_face_width(self) -> 'float':
        '''float: 'DistanceAlongFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceAlongFaceWidth

    @property
    def lead_relief(self) -> 'float':
        '''float: 'LeadRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeadRelief
