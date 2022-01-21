'''_4256.py

PartToPartShearCouplingHalfCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2329
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4126
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4213
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_HALF_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'PartToPartShearCouplingHalfCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingHalfCompoundParametricStudyTool',)


class PartToPartShearCouplingHalfCompoundParametricStudyTool(_4213.CouplingHalfCompoundParametricStudyTool):
    '''PartToPartShearCouplingHalfCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_HALF_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingHalfCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2329.PartToPartShearCouplingHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4126.PartToPartShearCouplingHalfParametricStudyTool]':
        '''List[PartToPartShearCouplingHalfParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4126.PartToPartShearCouplingHalfParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4126.PartToPartShearCouplingHalfParametricStudyTool]':
        '''List[PartToPartShearCouplingHalfParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4126.PartToPartShearCouplingHalfParametricStudyTool))
        return value
