'''_4072.py

CycloidalDiscParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.cycloidal import _2309
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6573
from mastapy.system_model.analyses_and_results.system_deflections import _2473
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4029
from mastapy._internal.python_net import python_net_import

_CYCLOIDAL_DISC_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'CycloidalDiscParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('CycloidalDiscParametricStudyTool',)


class CycloidalDiscParametricStudyTool(_4029.AbstractShaftParametricStudyTool):
    '''CycloidalDiscParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CYCLOIDAL_DISC_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CycloidalDiscParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2309.CycloidalDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6573.CycloidalDiscLoadCase':
        '''CycloidalDiscLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6573.CycloidalDiscLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_system_deflection_results(self) -> 'List[_2473.CycloidalDiscSystemDeflection]':
        '''List[CycloidalDiscSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2473.CycloidalDiscSystemDeflection))
        return value
