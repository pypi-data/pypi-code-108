'''_7114.py

TransmissionErrorToOtherPowerLoad
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1312
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TRANSMISSION_ERROR_TO_OTHER_POWER_LOAD = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections', 'TransmissionErrorToOtherPowerLoad')


__docformat__ = 'restructuredtext en'
__all__ = ('TransmissionErrorToOtherPowerLoad',)


class TransmissionErrorToOtherPowerLoad(_0.APIBase):
    '''TransmissionErrorToOtherPowerLoad

    This is a mastapy class.
    '''

    TYPE = _TRANSMISSION_ERROR_TO_OTHER_POWER_LOAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TransmissionErrorToOtherPowerLoad.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mean_te(self) -> 'float':
        '''float: 'MeanTE' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanTE

    @property
    def peak_to_peak_te(self) -> 'float':
        '''float: 'PeakToPeakTE' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeakToPeakTE

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def fourier_series_of_te(self) -> '_1312.FourierSeries':
        '''FourierSeries: 'FourierSeriesOfTE' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1312.FourierSeries)(self.wrapped.FourierSeriesOfTE) if self.wrapped.FourierSeriesOfTE is not None else None
