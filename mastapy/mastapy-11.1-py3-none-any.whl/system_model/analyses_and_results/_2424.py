'''_2424.py

TimeOptions
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TIME_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'TimeOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('TimeOptions',)


class TimeOptions(_0.APIBase):
    '''TimeOptions

    This is a mastapy class.
    '''

    TYPE = _TIME_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TimeOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def end_time(self) -> 'float':
        '''float: 'EndTime' is the original name of this property.'''

        return self.wrapped.EndTime

    @end_time.setter
    def end_time(self, value: 'float'):
        self.wrapped.EndTime = float(value) if value else 0.0

    @property
    def start_time(self) -> 'float':
        '''float: 'StartTime' is the original name of this property.'''

        return self.wrapped.StartTime

    @start_time.setter
    def start_time(self, value: 'float'):
        self.wrapped.StartTime = float(value) if value else 0.0

    @property
    def total_time(self) -> 'float':
        '''float: 'TotalTime' is the original name of this property.'''

        return self.wrapped.TotalTime

    @total_time.setter
    def total_time(self, value: 'float'):
        self.wrapped.TotalTime = float(value) if value else 0.0
