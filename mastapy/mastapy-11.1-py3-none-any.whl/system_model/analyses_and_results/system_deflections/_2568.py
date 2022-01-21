'''_2568.py

TransmissionErrorResult
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TRANSMISSION_ERROR_RESULT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'TransmissionErrorResult')


__docformat__ = 'restructuredtext en'
__all__ = ('TransmissionErrorResult',)


class TransmissionErrorResult(_0.APIBase):
    '''TransmissionErrorResult

    This is a mastapy class.
    '''

    TYPE = _TRANSMISSION_ERROR_RESULT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TransmissionErrorResult.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def transmission_error(self) -> 'float':
        '''float: 'TransmissionError' is the original name of this property.'''

        return self.wrapped.TransmissionError

    @transmission_error.setter
    def transmission_error(self, value: 'float'):
        self.wrapped.TransmissionError = float(value) if value else 0.0
