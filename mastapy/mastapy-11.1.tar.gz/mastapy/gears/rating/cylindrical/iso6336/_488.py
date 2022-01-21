'''_488.py

ToothFlankFractureAnalysisContactPointN1457
'''


from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy._math.vector_2d import Vector2D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TOOTH_FLANK_FRACTURE_ANALYSIS_CONTACT_POINT_N1457 = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ToothFlankFractureAnalysisContactPointN1457')


__docformat__ = 'restructuredtext en'
__all__ = ('ToothFlankFractureAnalysisContactPointN1457',)


class ToothFlankFractureAnalysisContactPointN1457(_0.APIBase):
    '''ToothFlankFractureAnalysisContactPointN1457

    This is a mastapy class.
    '''

    TYPE = _TOOTH_FLANK_FRACTURE_ANALYSIS_CONTACT_POINT_N1457

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToothFlankFractureAnalysisContactPointN1457.TYPE'):
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
    def half_of_hertzian_contact_width(self) -> 'float':
        '''float: 'HalfOfHertzianContactWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HalfOfHertzianContactWidth

    @property
    def mean_coefficient_of_friction(self) -> 'float':
        '''float: 'MeanCoefficientOfFriction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFriction

    @property
    def position_on_profile(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'PositionOnProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.PositionOnProfile) if self.wrapped.PositionOnProfile is not None else None

    @property
    def coordinates(self) -> 'Vector2D':
        '''Vector2D: 'Coordinates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.Coordinates)
        return value
