'''_5831.py

DatapointForResponseOfAComponentOrSurfaceAtAFrequencyInAHarmonic
'''


from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DATAPOINT_FOR_RESPONSE_OF_A_COMPONENT_OR_SURFACE_AT_A_FREQUENCY_IN_A_HARMONIC = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.ReportablePropertyResults', 'DatapointForResponseOfAComponentOrSurfaceAtAFrequencyInAHarmonic')


__docformat__ = 'restructuredtext en'
__all__ = ('DatapointForResponseOfAComponentOrSurfaceAtAFrequencyInAHarmonic',)


class DatapointForResponseOfAComponentOrSurfaceAtAFrequencyInAHarmonic(_0.APIBase):
    '''DatapointForResponseOfAComponentOrSurfaceAtAFrequencyInAHarmonic

    This is a mastapy class.
    '''

    TYPE = _DATAPOINT_FOR_RESPONSE_OF_A_COMPONENT_OR_SURFACE_AT_A_FREQUENCY_IN_A_HARMONIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatapointForResponseOfAComponentOrSurfaceAtAFrequencyInAHarmonic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def speed(self) -> 'float':
        '''float: 'Speed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Speed

    @property
    def frequency(self) -> 'float':
        '''float: 'Frequency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Frequency

    @property
    def response(self) -> 'complex':
        '''complex: 'Response' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_complex(self.wrapped.Response)
        return value
