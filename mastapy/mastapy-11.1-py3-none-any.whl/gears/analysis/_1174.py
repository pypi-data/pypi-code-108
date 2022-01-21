'''_1174.py

GearSetImplementationAnalysisDutyCycle
'''


from mastapy._internal import constructor
from mastapy.gears.analysis import _1173
from mastapy._internal.python_net import python_net_import

_GEAR_SET_IMPLEMENTATION_ANALYSIS_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.Analysis', 'GearSetImplementationAnalysisDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetImplementationAnalysisDutyCycle',)


class GearSetImplementationAnalysisDutyCycle(_1173.GearSetImplementationAnalysisAbstract):
    '''GearSetImplementationAnalysisDutyCycle

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_IMPLEMENTATION_ANALYSIS_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetImplementationAnalysisDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def duty_cycle_name(self) -> 'str':
        '''str: 'DutyCycleName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DutyCycleName
