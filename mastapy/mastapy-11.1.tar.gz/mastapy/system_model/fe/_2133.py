'''_2133.py

FESubstructureWithSelectionForHarmonicAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.nodal_analysis.dev_tools_analyses import _161
from mastapy.system_model.fe import _2141, _2131
from mastapy._internal.python_net import python_net_import

_FE_SUBSTRUCTURE_WITH_SELECTION_FOR_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FESubstructureWithSelectionForHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FESubstructureWithSelectionForHarmonicAnalysis',)


class FESubstructureWithSelectionForHarmonicAnalysis(_2131.FESubstructureWithSelection):
    '''FESubstructureWithSelectionForHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _FE_SUBSTRUCTURE_WITH_SELECTION_FOR_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FESubstructureWithSelectionForHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def frequency(self) -> 'float':
        '''float: 'Frequency' is the original name of this property.'''

        return self.wrapped.Frequency

    @frequency.setter
    def frequency(self, value: 'float'):
        self.wrapped.Frequency = float(value) if value else 0.0

    @property
    def alpha_damping_value(self) -> 'float':
        '''float: 'AlphaDampingValue' is the original name of this property.'''

        return self.wrapped.AlphaDampingValue

    @alpha_damping_value.setter
    def alpha_damping_value(self, value: 'float'):
        self.wrapped.AlphaDampingValue = float(value) if value else 0.0

    @property
    def beta_damping_value(self) -> 'float':
        '''float: 'BetaDampingValue' is the original name of this property.'''

        return self.wrapped.BetaDampingValue

    @beta_damping_value.setter
    def beta_damping_value(self, value: 'float'):
        self.wrapped.BetaDampingValue = float(value) if value else 0.0

    @property
    def harmonic_draw_style(self) -> '_161.FEModelHarmonicAnalysisDrawStyle':
        '''FEModelHarmonicAnalysisDrawStyle: 'HarmonicDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_161.FEModelHarmonicAnalysisDrawStyle)(self.wrapped.HarmonicDrawStyle) if self.wrapped.HarmonicDrawStyle is not None else None

    @property
    def boundary_conditions_all_nodes(self) -> 'List[_2141.NodeBoundaryConditionStaticAnalysis]':
        '''List[NodeBoundaryConditionStaticAnalysis]: 'BoundaryConditionsAllNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoundaryConditionsAllNodes, constructor.new(_2141.NodeBoundaryConditionStaticAnalysis))
        return value

    def solve_for_current_inputs(self):
        ''' 'SolveForCurrentInputs' is the original name of this method.'''

        self.wrapped.SolveForCurrentInputs()

    def export_velocity_to_file(self):
        ''' 'ExportVelocityToFile' is the original name of this method.'''

        self.wrapped.ExportVelocityToFile()
