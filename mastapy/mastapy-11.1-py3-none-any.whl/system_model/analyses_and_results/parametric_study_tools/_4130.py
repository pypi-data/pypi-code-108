'''_4130.py

PlanetCarrierParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2210
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6653
from mastapy.system_model.analyses_and_results.system_deflections import _2525
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4112
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'PlanetCarrierParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierParametricStudyTool',)


class PlanetCarrierParametricStudyTool(_4112.MountableComponentParametricStudyTool):
    '''PlanetCarrierParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2210.PlanetCarrier':
        '''PlanetCarrier: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2210.PlanetCarrier)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6653.PlanetCarrierLoadCase':
        '''PlanetCarrierLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6653.PlanetCarrierLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def component_system_deflection_results(self) -> 'List[_2525.PlanetCarrierSystemDeflection]':
        '''List[PlanetCarrierSystemDeflection]: 'ComponentSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentSystemDeflectionResults, constructor.new(_2525.PlanetCarrierSystemDeflection))
        return value
