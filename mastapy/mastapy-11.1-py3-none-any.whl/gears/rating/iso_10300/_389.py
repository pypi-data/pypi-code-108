'''_389.py

Iso10300MeshSingleFlankRatingBevelMethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.iso_10300 import _392
from mastapy._internal.python_net import python_net_import

_ISO_10300_MESH_SINGLE_FLANK_RATING_BEVEL_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'Iso10300MeshSingleFlankRatingBevelMethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('Iso10300MeshSingleFlankRatingBevelMethodB2',)


class Iso10300MeshSingleFlankRatingBevelMethodB2(_392.ISO10300MeshSingleFlankRatingMethodB2):
    '''Iso10300MeshSingleFlankRatingBevelMethodB2

    This is a mastapy class.
    '''

    TYPE = _ISO_10300_MESH_SINGLE_FLANK_RATING_BEVEL_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Iso10300MeshSingleFlankRatingBevelMethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def location_of_point_of_load_application_for_maximum_bending_stress_on_path_of_action_for_non_statically_loaded_with_modified_contact_ratio_less_or_equal_than_2(self) -> 'float':
        '''float: 'LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfActionForNonStaticallyLoadedWithModifiedContactRatioLessOrEqualThan2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfActionForNonStaticallyLoadedWithModifiedContactRatioLessOrEqualThan2

    @property
    def location_of_point_of_load_application_for_maximum_bending_stress_on_path_of_action_for_non_statically_loaded_with_modified_contact_ratio_larger_than_2(self) -> 'float':
        '''float: 'LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfActionForNonStaticallyLoadedWithModifiedContactRatioLargerThan2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfActionForNonStaticallyLoadedWithModifiedContactRatioLargerThan2

    @property
    def location_of_point_of_load_application_for_maximum_bending_stress_on_path_of_action_for_statically_loaded_straight_bevel_and_zerol_bevel_gear(self) -> 'float':
        '''float: 'LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfActionForStaticallyLoadedStraightBevelAndZerolBevelGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfActionForStaticallyLoadedStraightBevelAndZerolBevelGear

    @property
    def location_of_point_of_load_application_for_maximum_bending_stress_on_path_of_action(self) -> 'float':
        '''float: 'LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocationOfPointOfLoadApplicationForMaximumBendingStressOnPathOfAction

    @property
    def relative_length_of_action_to_point_of_load_application_method_b2(self) -> 'float':
        '''float: 'RelativeLengthOfActionToPointOfLoadApplicationMethodB2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeLengthOfActionToPointOfLoadApplicationMethodB2

    @property
    def gj(self) -> 'float':
        '''float: 'GJ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GJ

    @property
    def load_sharing_ratio_for_bending_method_b2_for_none_statically_loaded_bevel_gear(self) -> 'float':
        '''float: 'LoadSharingRatioForBendingMethodB2ForNoneStaticallyLoadedBevelGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioForBendingMethodB2ForNoneStaticallyLoadedBevelGear

    @property
    def load_sharing_ratio_for_bending_method_b2_statically_loaded_straight_and_zerol_bevel_gears(self) -> 'float':
        '''float: 'LoadSharingRatioForBendingMethodB2StaticallyLoadedStraightAndZerolBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioForBendingMethodB2StaticallyLoadedStraightAndZerolBevelGears
