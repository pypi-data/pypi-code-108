'''_4149.py

SpringDamperParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2340
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6677
from mastapy.system_model.analyses_and_results.system_deflections import _2547
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4066
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'SpringDamperParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperParametricStudyTool',)


class SpringDamperParametricStudyTool(_4066.CouplingParametricStudyTool):
    '''SpringDamperParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2340.SpringDamper':
        '''SpringDamper: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2340.SpringDamper)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6677.SpringDamperLoadCase':
        '''SpringDamperLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6677.SpringDamperLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def assembly_system_deflection_results(self) -> 'List[_2547.SpringDamperSystemDeflection]':
        '''List[SpringDamperSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2547.SpringDamperSystemDeflection))
        return value
