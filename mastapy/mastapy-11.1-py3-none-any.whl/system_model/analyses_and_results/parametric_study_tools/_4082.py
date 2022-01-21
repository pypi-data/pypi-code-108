'''_4082.py

DutyCycleResultsForAllGearSets
'''


from mastapy.gears.analysis import _1171
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DUTY_CYCLE_RESULTS_FOR_ALL_GEAR_SETS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'DutyCycleResultsForAllGearSets')


__docformat__ = 'restructuredtext en'
__all__ = ('DutyCycleResultsForAllGearSets',)


class DutyCycleResultsForAllGearSets(_0.APIBase):
    '''DutyCycleResultsForAllGearSets

    This is a mastapy class.
    '''

    TYPE = _DUTY_CYCLE_RESULTS_FOR_ALL_GEAR_SETS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DutyCycleResultsForAllGearSets.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def duty_cycle_results(self) -> '_1171.GearSetGroupDutyCycle':
        '''GearSetGroupDutyCycle: 'DutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1171.GearSetGroupDutyCycle)(self.wrapped.DutyCycleResults) if self.wrapped.DutyCycleResults is not None else None
