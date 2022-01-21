'''_4257.py

PlanetaryConnectionCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.connections_and_sockets import _2029
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4128
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4271
from mastapy._internal.python_net import python_net_import

_PLANETARY_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'PlanetaryConnectionCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryConnectionCompoundParametricStudyTool',)


class PlanetaryConnectionCompoundParametricStudyTool(_4271.ShaftToMountableComponentConnectionCompoundParametricStudyTool):
    '''PlanetaryConnectionCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryConnectionCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2029.PlanetaryConnection)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def connection_design(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2029.PlanetaryConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4128.PlanetaryConnectionParametricStudyTool]':
        '''List[PlanetaryConnectionParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4128.PlanetaryConnectionParametricStudyTool))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_4128.PlanetaryConnectionParametricStudyTool]':
        '''List[PlanetaryConnectionParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4128.PlanetaryConnectionParametricStudyTool))
        return value
