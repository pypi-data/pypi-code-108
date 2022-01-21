'''_7262.py

PartAnalysisCase
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results import _2397
from mastapy._internal.python_net import python_net_import

_PART_ANALYSIS_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'PartAnalysisCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PartAnalysisCase',)


class PartAnalysisCase(_2397.PartAnalysis):
    '''PartAnalysisCase

    This is a mastapy class.
    '''

    TYPE = _PART_ANALYSIS_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartAnalysisCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def three_d_isometric_view(self) -> 'Image':
        '''Image: 'ThreeDIsometricView' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDIsometricView)
        return value

    @property
    def three_d_view_orientated_in_xy_plane_with_z_axis_pointing_out_of_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXyPlaneWithZAxisPointingOutOfTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXyPlaneWithZAxisPointingOutOfTheScreen)
        return value

    @property
    def three_d_view_orientated_in_xy_plane_with_z_axis_pointing_into_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXyPlaneWithZAxisPointingIntoTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXyPlaneWithZAxisPointingIntoTheScreen)
        return value

    @property
    def three_d_view_orientated_in_yz_plane_with_x_axis_pointing_into_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInYzPlaneWithXAxisPointingIntoTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInYzPlaneWithXAxisPointingIntoTheScreen)
        return value

    @property
    def three_d_view_orientated_in_yz_plane_with_x_axis_pointing_out_of_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInYzPlaneWithXAxisPointingOutOfTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInYzPlaneWithXAxisPointingOutOfTheScreen)
        return value

    @property
    def three_d_view_orientated_in_xz_plane_with_y_axis_pointing_into_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXzPlaneWithYAxisPointingIntoTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXzPlaneWithYAxisPointingIntoTheScreen)
        return value

    @property
    def three_d_view_orientated_in_xz_plane_with_y_axis_pointing_out_of_the_screen(self) -> 'Image':
        '''Image: 'ThreeDViewOrientatedInXzPlaneWithYAxisPointingOutOfTheScreen' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDViewOrientatedInXzPlaneWithYAxisPointingOutOfTheScreen)
        return value

    @property
    def three_d_view(self) -> 'Image':
        '''Image: 'ThreeDView' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ThreeDView)
        return value
