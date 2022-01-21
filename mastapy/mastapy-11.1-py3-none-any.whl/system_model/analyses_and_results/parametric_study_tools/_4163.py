'''_4163.py

TorqueConverterParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2347
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6692
from mastapy.system_model.analyses_and_results.system_deflections import _2565
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4066
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'TorqueConverterParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterParametricStudyTool',)


class TorqueConverterParametricStudyTool(_4066.CouplingParametricStudyTool):
    '''TorqueConverterParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2347.TorqueConverter':
        '''TorqueConverter: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2347.TorqueConverter)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6692.TorqueConverterLoadCase':
        '''TorqueConverterLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6692.TorqueConverterLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def assembly_system_deflection_results(self) -> 'List[_2565.TorqueConverterSystemDeflection]':
        '''List[TorqueConverterSystemDeflection]: 'AssemblySystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblySystemDeflectionResults, constructor.new(_2565.TorqueConverterSystemDeflection))
        return value
