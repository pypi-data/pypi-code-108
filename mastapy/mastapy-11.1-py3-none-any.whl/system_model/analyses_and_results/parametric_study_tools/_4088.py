'''_4088.py

FaceGearParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model.gears import _2268
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6599
from mastapy.system_model.analyses_and_results.system_deflections import _2491
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4093
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'FaceGearParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearParametricStudyTool',)


class FaceGearParametricStudyTool(_4093.GearParametricStudyTool):
    '''FaceGearParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2268.FaceGear':
        '''FaceGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2268.FaceGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6599.FaceGearLoadCase':
        '''FaceGearLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6599.FaceGearLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_system_deflection_results(self) -> 'List[_2491.FaceGearSystemDeflection]':
        '''List[FaceGearSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2491.FaceGearSystemDeflection))
        return value
