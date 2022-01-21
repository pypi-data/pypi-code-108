'''_4148.py

SpringDamperHalfParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2341
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6676
from mastapy.system_model.analyses_and_results.system_deflections import _2546
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4065
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_HALF_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'SpringDamperHalfParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperHalfParametricStudyTool',)


class SpringDamperHalfParametricStudyTool(_4065.CouplingHalfParametricStudyTool):
    '''SpringDamperHalfParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_HALF_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperHalfParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2341.SpringDamperHalf':
        '''SpringDamperHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2341.SpringDamperHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6676.SpringDamperHalfLoadCase':
        '''SpringDamperHalfLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6676.SpringDamperHalfLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_system_deflection_results(self) -> 'List[_2546.SpringDamperHalfSystemDeflection]':
        '''List[SpringDamperHalfSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2546.SpringDamperHalfSystemDeflection))
        return value
