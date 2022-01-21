'''_6715.py

MultiTimeSeriesDataInputFileOptions
'''


from mastapy._internal import constructor
from mastapy.utility.file_access_helpers import _1587
from mastapy.utility_gui import _1615
from mastapy._internal.python_net import python_net_import

_MULTI_TIME_SERIES_DATA_INPUT_FILE_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'MultiTimeSeriesDataInputFileOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('MultiTimeSeriesDataInputFileOptions',)


class MultiTimeSeriesDataInputFileOptions(_1615.DataInputFileOptions):
    '''MultiTimeSeriesDataInputFileOptions

    This is a mastapy class.
    '''

    TYPE = _MULTI_TIME_SERIES_DATA_INPUT_FILE_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MultiTimeSeriesDataInputFileOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def duration_scaling(self) -> 'float':
        '''float: 'DurationScaling' is the original name of this property.'''

        return self.wrapped.DurationScaling

    @duration_scaling.setter
    def duration_scaling(self, value: 'float'):
        self.wrapped.DurationScaling = float(value) if value else 0.0

    @property
    def proportion_of_duty_cycle(self) -> 'float':
        '''float: 'ProportionOfDutyCycle' is the original name of this property.'''

        return self.wrapped.ProportionOfDutyCycle

    @proportion_of_duty_cycle.setter
    def proportion_of_duty_cycle(self, value: 'float'):
        self.wrapped.ProportionOfDutyCycle = float(value) if value else 0.0

    @property
    def duration(self) -> 'float':
        '''float: 'Duration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Duration

    @property
    def delimiter_options(self) -> '_1587.TextFileDelimiterOptions':
        '''TextFileDelimiterOptions: 'DelimiterOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1587.TextFileDelimiterOptions)(self.wrapped.DelimiterOptions) if self.wrapped.DelimiterOptions is not None else None
