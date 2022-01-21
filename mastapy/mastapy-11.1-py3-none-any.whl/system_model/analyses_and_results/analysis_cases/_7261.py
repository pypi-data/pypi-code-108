'''_7261.py

FEAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.analysis_cases import _7267
from mastapy._internal.python_net import python_net_import

_FE_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'FEAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FEAnalysis',)


class FEAnalysis(_7267.StaticLoadAnalysisCase):
    '''FEAnalysis

    This is a mastapy class.
    '''

    TYPE = _FE_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def stiffness_with_respect_to_input_power_load(self) -> 'float':
        '''float: 'StiffnessWithRespectToInputPowerLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessWithRespectToInputPowerLoad

    @property
    def torque_ratio_to_output(self) -> 'float':
        '''float: 'TorqueRatioToOutput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueRatioToOutput

    @property
    def torque_at_zero_displacement_for_input_power_load(self) -> 'float':
        '''float: 'TorqueAtZeroDisplacementForInputPowerLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueAtZeroDisplacementForInputPowerLoad
