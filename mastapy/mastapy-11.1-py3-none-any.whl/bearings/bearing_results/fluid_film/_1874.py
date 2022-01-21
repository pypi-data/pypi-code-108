'''_1874.py

LoadedPlainOilFedJournalBearingRow
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_results.fluid_film import _1872
from mastapy._internal.python_net import python_net_import

_LOADED_PLAIN_OIL_FED_JOURNAL_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.FluidFilm', 'LoadedPlainOilFedJournalBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedPlainOilFedJournalBearingRow',)


class LoadedPlainOilFedJournalBearingRow(_1872.LoadedPlainJournalBearingRow):
    '''LoadedPlainOilFedJournalBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_PLAIN_OIL_FED_JOURNAL_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedPlainOilFedJournalBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def non_dimensional_misalignment(self) -> 'float':
        '''float: 'NonDimensionalMisalignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NonDimensionalMisalignment

    @property
    def misalignment_angle(self) -> 'float':
        '''float: 'MisalignmentAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MisalignmentAngle

    @property
    def load_correction_factor(self) -> 'float':
        '''float: 'LoadCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadCorrectionFactor

    @property
    def power_correction_factor(self) -> 'float':
        '''float: 'PowerCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PowerCorrectionFactor

    @property
    def attitude_correction_factor(self) -> 'float':
        '''float: 'AttitudeCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AttitudeCorrectionFactor

    @property
    def side_flow_correction_factor(self) -> 'float':
        '''float: 'SideFlowCorrectionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SideFlowCorrectionFactor

    @property
    def pressure_distribution(self) -> 'Image':
        '''Image: 'PressureDistribution' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.PressureDistribution)
        return value
