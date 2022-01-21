'''_5249.py

DynamicForceResultAtTime
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses.reporting import _5248
from mastapy._internal.python_net import python_net_import

_DYNAMIC_FORCE_RESULT_AT_TIME = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Reporting', 'DynamicForceResultAtTime')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicForceResultAtTime',)


class DynamicForceResultAtTime(_5248.AbstractMeasuredDynamicResponseAtTime):
    '''DynamicForceResultAtTime

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_FORCE_RESULT_AT_TIME

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicForceResultAtTime.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def dynamic_force(self) -> 'float':
        '''float: 'DynamicForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicForce

    @property
    def mean_force(self) -> 'float':
        '''float: 'MeanForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanForce

    @property
    def force(self) -> 'float':
        '''float: 'Force' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Force

    @property
    def absolute_dynamic_force(self) -> 'float':
        '''float: 'AbsoluteDynamicForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteDynamicForce
