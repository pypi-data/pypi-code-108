'''_4110.py

MeasurementComponentParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2204
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6639
from mastapy.system_model.analyses_and_results.system_deflections import _2515
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4167
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_COMPONENT_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'MeasurementComponentParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementComponentParametricStudyTool',)


class MeasurementComponentParametricStudyTool(_4167.VirtualComponentParametricStudyTool):
    '''MeasurementComponentParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_COMPONENT_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementComponentParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2204.MeasurementComponent)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6639.MeasurementComponentLoadCase':
        '''MeasurementComponentLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6639.MeasurementComponentLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_system_deflection_results(self) -> 'List[_2515.MeasurementComponentSystemDeflection]':
        '''List[MeasurementComponentSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2515.MeasurementComponentSystemDeflection))
        return value
