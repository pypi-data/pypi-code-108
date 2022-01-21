'''_3418.py

CylindricalGearSetCompoundSteadyStateSynchronousResponse
'''


from typing import List

from mastapy.system_model.part_model.gears import _2266, _2282
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.compound import _3416, _3417, _3429
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3284
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound', 'CylindricalGearSetCompoundSteadyStateSynchronousResponse')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetCompoundSteadyStateSynchronousResponse',)


class CylindricalGearSetCompoundSteadyStateSynchronousResponse(_3429.GearSetCompoundSteadyStateSynchronousResponse):
    '''CylindricalGearSetCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetCompoundSteadyStateSynchronousResponse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to CylindricalGearSet. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2266.CylindricalGearSet':
        '''CylindricalGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2266.CylindricalGearSet.TYPE not in self.wrapped.AssemblyDesign.__class__.__mro__:
            raise CastException('Failed to cast assembly_design to CylindricalGearSet. Expected: {}.'.format(self.wrapped.AssemblyDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AssemblyDesign.__class__)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def cylindrical_gears_compound_steady_state_synchronous_response(self) -> 'List[_3416.CylindricalGearCompoundSteadyStateSynchronousResponse]':
        '''List[CylindricalGearCompoundSteadyStateSynchronousResponse]: 'CylindricalGearsCompoundSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearsCompoundSteadyStateSynchronousResponse, constructor.new(_3416.CylindricalGearCompoundSteadyStateSynchronousResponse))
        return value

    @property
    def cylindrical_meshes_compound_steady_state_synchronous_response(self) -> 'List[_3417.CylindricalGearMeshCompoundSteadyStateSynchronousResponse]':
        '''List[CylindricalGearMeshCompoundSteadyStateSynchronousResponse]: 'CylindricalMeshesCompoundSteadyStateSynchronousResponse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshesCompoundSteadyStateSynchronousResponse, constructor.new(_3417.CylindricalGearMeshCompoundSteadyStateSynchronousResponse))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3284.CylindricalGearSetSteadyStateSynchronousResponse]':
        '''List[CylindricalGearSetSteadyStateSynchronousResponse]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3284.CylindricalGearSetSteadyStateSynchronousResponse))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3284.CylindricalGearSetSteadyStateSynchronousResponse]':
        '''List[CylindricalGearSetSteadyStateSynchronousResponse]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3284.CylindricalGearSetSteadyStateSynchronousResponse))
        return value
