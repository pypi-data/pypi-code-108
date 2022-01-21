'''_4234.py

GearSetCompoundParametricStudyTool
'''


from typing import List

from mastapy.gears.rating import _328
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.worm import _341
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.face import _415
from mastapy.gears.rating.cylindrical import _427
from mastapy.gears.rating.conical import _501
from mastapy.gears.rating.concept import _512
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4094
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4272
from mastapy._internal.python_net import python_net_import

_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'GearSetCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetCompoundParametricStudyTool',)


class GearSetCompoundParametricStudyTool(_4272.SpecialisedAssemblyCompoundParametricStudyTool):
    '''GearSetCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_set_duty_cycle_results(self) -> '_328.GearSetDutyCycleRating':
        '''GearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _328.GearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to GearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults is not None else None

    @property
    def gear_set_duty_cycle_results_of_type_worm_gear_set_duty_cycle_rating(self) -> '_341.WormGearSetDutyCycleRating':
        '''WormGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _341.WormGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to WormGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults is not None else None

    @property
    def gear_set_duty_cycle_results_of_type_face_gear_set_duty_cycle_rating(self) -> '_415.FaceGearSetDutyCycleRating':
        '''FaceGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _415.FaceGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to FaceGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults is not None else None

    @property
    def gear_set_duty_cycle_results_of_type_cylindrical_gear_set_duty_cycle_rating(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _427.CylindricalGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to CylindricalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults is not None else None

    @property
    def gear_set_duty_cycle_results_of_type_conical_gear_set_duty_cycle_rating(self) -> '_501.ConicalGearSetDutyCycleRating':
        '''ConicalGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _501.ConicalGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to ConicalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults is not None else None

    @property
    def gear_set_duty_cycle_results_of_type_concept_gear_set_duty_cycle_rating(self) -> '_512.ConceptGearSetDutyCycleRating':
        '''ConceptGearSetDutyCycleRating: 'GearSetDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _512.ConceptGearSetDutyCycleRating.TYPE not in self.wrapped.GearSetDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_set_duty_cycle_results to ConceptGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.GearSetDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetDutyCycleResults.__class__)(self.wrapped.GearSetDutyCycleResults) if self.wrapped.GearSetDutyCycleResults is not None else None

    @property
    def assembly_analysis_cases(self) -> 'List[_4094.GearSetParametricStudyTool]':
        '''List[GearSetParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4094.GearSetParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4094.GearSetParametricStudyTool]':
        '''List[GearSetParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4094.GearSetParametricStudyTool))
        return value
