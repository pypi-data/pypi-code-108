'''_1768.py

LoadedMultiPointContactBallBearingElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1749
from mastapy._internal.python_net import python_net_import

_LOADED_MULTI_POINT_CONTACT_BALL_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedMultiPointContactBallBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedMultiPointContactBallBearingElement',)


class LoadedMultiPointContactBallBearingElement(_1749.LoadedBallBearingElement):
    '''LoadedMultiPointContactBallBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_MULTI_POINT_CONTACT_BALL_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedMultiPointContactBallBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def normal_load_inner_left(self) -> 'float':
        '''float: 'NormalLoadInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalLoadInnerLeft

    @property
    def normal_load_inner_right(self) -> 'float':
        '''float: 'NormalLoadInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalLoadInnerRight

    @property
    def contact_angle_inner_left(self) -> 'float':
        '''float: 'ContactAngleInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactAngleInnerLeft

    @property
    def contact_angle_inner_right(self) -> 'float':
        '''float: 'ContactAngleInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactAngleInnerRight

    @property
    def maximum_normal_stress_inner(self) -> 'float':
        '''float: 'MaximumNormalStressInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressInner

    @property
    def maximum_normal_stress_inner_left(self) -> 'float':
        '''float: 'MaximumNormalStressInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressInnerLeft

    @property
    def maximum_normal_stress_inner_right(self) -> 'float':
        '''float: 'MaximumNormalStressInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumNormalStressInnerRight

    @property
    def maximum_shear_stress_inner_left(self) -> 'float':
        '''float: 'MaximumShearStressInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumShearStressInnerLeft

    @property
    def maximum_shear_stress_inner_right(self) -> 'float':
        '''float: 'MaximumShearStressInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumShearStressInnerRight

    @property
    def minimum_lubricating_film_thickness_inner_left(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessInnerLeft

    @property
    def minimum_lubricating_film_thickness_inner_right(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessInnerRight

    @property
    def minimum_lubricating_film_thickness_inner(self) -> 'float':
        '''float: 'MinimumLubricatingFilmThicknessInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumLubricatingFilmThicknessInner

    @property
    def hertzian_semi_major_dimension_inner_left(self) -> 'float':
        '''float: 'HertzianSemiMajorDimensionInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMajorDimensionInnerLeft

    @property
    def hertzian_semi_minor_dimension_inner_left(self) -> 'float':
        '''float: 'HertzianSemiMinorDimensionInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMinorDimensionInnerLeft

    @property
    def hertzian_semi_major_dimension_inner_right(self) -> 'float':
        '''float: 'HertzianSemiMajorDimensionInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMajorDimensionInnerRight

    @property
    def hertzian_semi_minor_dimension_inner_right(self) -> 'float':
        '''float: 'HertzianSemiMinorDimensionInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HertzianSemiMinorDimensionInnerRight
