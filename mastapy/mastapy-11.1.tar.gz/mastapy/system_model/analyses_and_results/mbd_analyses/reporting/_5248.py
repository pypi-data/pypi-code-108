'''_5248.py

AbstractMeasuredDynamicResponseAtTime
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_MEASURED_DYNAMIC_RESPONSE_AT_TIME = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Reporting', 'AbstractMeasuredDynamicResponseAtTime')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractMeasuredDynamicResponseAtTime',)


class AbstractMeasuredDynamicResponseAtTime(_0.APIBase):
    '''AbstractMeasuredDynamicResponseAtTime

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_MEASURED_DYNAMIC_RESPONSE_AT_TIME

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractMeasuredDynamicResponseAtTime.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def time(self) -> 'float':
        '''float: 'Time' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Time

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def percentage_increase(self) -> 'float':
        '''float: 'PercentageIncrease' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageIncrease
