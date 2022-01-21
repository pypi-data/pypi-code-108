'''_1764.py

LoadedFourPointContactBallBearingElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1768
from mastapy._internal.python_net import python_net_import

_LOADED_FOUR_POINT_CONTACT_BALL_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedFourPointContactBallBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedFourPointContactBallBearingElement',)


class LoadedFourPointContactBallBearingElement(_1768.LoadedMultiPointContactBallBearingElement):
    '''LoadedFourPointContactBallBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_FOUR_POINT_CONTACT_BALL_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedFourPointContactBallBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def normal_load_outer_right(self) -> 'float':
        '''float: 'NormalLoadOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalLoadOuterRight

    @property
    def normal_load_outer_left(self) -> 'float':
        '''float: 'NormalLoadOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalLoadOuterLeft

    @property
    def contact_angle_outer_left(self) -> 'float':
        '''float: 'ContactAngleOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactAngleOuterLeft

    @property
    def contact_angle_outer_right(self) -> 'float':
        '''float: 'ContactAngleOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactAngleOuterRight

    @property
    def maximum_normal_stress_outer(self) -> 'float':
        '''float: 'MaximumNormalStressOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressOuter

    @property
    def maximum_normal_stress_outer_left(self) -> 'float':
        '''float: 'MaximumNormalStressOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressOuterLeft

    @property
    def maximum_normal_stress_outer_right(self) -> 'float':
        '''float: 'MaximumNormalStressOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressOuterRight

    @property
    def maximum_shear_stress_outer_left(self) -> 'float':
        '''float: 'MaximumShearStressOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumShearStressOuterLeft

    @property
    def maximum_shear_stress_outer_right(self) -> 'float':
        '''float: 'MaximumShearStressOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumShearStressOuterRight

    @property
    def minimum_lubricating_film_thickness_outer_left(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessOuterLeft

    @property
    def minimum_lubricating_film_thickness_outer_right(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessOuterRight

    @property
    def minimum_lubricating_film_thickness_outer(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessOuter

    @property
    def hertzian_semi_major_dimension_outer_left(self) -> 'float':
        '''float: 'HertzianSemiMajorDimensionOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMajorDimensionOuterLeft

    @property
    def hertzian_semi_minor_dimension_outer_left(self) -> 'float':
        '''float: 'HertzianSemiMinorDimensionOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMinorDimensionOuterLeft

    @property
    def hertzian_semi_major_dimension_outer_right(self) -> 'float':
        '''float: 'HertzianSemiMajorDimensionOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMajorDimensionOuterRight

    @property
    def hertzian_semi_minor_dimension_outer_right(self) -> 'float':
        '''float: 'HertzianSemiMinorDimensionOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMinorDimensionOuterRight
