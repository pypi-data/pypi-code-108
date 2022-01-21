'''_2512.py

LoadCaseOverallEfficiencyResult
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_LOAD_CASE_OVERALL_EFFICIENCY_RESULT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'LoadCaseOverallEfficiencyResult')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadCaseOverallEfficiencyResult',)


class LoadCaseOverallEfficiencyResult(_0.APIBase):
    '''LoadCaseOverallEfficiencyResult

    This is a mastapy class.
    '''

    TYPE = _LOAD_CASE_OVERALL_EFFICIENCY_RESULT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadCaseOverallEfficiencyResult.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def energy_input(self) -> 'float':
        '''float: 'EnergyInput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyInput

    @property
    def energy_lost(self) -> 'float':
        '''float: 'EnergyLost' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyLost

    @property
    def energy_output(self) -> 'float':
        '''float: 'EnergyOutput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyOutput

    @property
    def efficiency(self) -> 'float':
        '''float: 'Efficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Efficiency

    @property
    def duration(self) -> 'float':
        '''float: 'Duration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Duration

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
