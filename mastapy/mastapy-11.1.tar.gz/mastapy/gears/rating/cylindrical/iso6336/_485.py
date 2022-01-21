'''_485.py

ToothFlankFractureAnalysisContactPoint
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _486
from mastapy._internal.python_net import python_net_import

_TOOTH_FLANK_FRACTURE_ANALYSIS_CONTACT_POINT = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ToothFlankFractureAnalysisContactPoint')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothFlankFractureAnalysisContactPoint',)


class ToothFlankFractureAnalysisContactPoint(_486.ToothFlankFractureAnalysisContactPointCommon):
    '''ToothFlankFractureAnalysisContactPoint

    This is a mastapy class.
    '''

    TYPE = _TOOTH_FLANK_FRACTURE_ANALYSIS_CONTACT_POINT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothFlankFractureAnalysisContactPoint.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hertzian_contact_stress(self) -> 'float':
        '''float: 'HertzianContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianContactStress

    @property
    def local_normal_radius_of_relative_curvature(self) -> 'float':
        '''float: 'LocalNormalRadiusOfRelativeCurvature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalNormalRadiusOfRelativeCurvature

    @property
    def half_of_hertzian_contact_width(self) -> 'float':
        '''float: 'HalfOfHertzianContactWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HalfOfHertzianContactWidth
