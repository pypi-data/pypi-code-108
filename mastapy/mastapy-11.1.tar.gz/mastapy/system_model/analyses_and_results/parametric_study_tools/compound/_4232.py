'''_4232.py

GearCompoundParametricStudyTool
'''


from typing import List

from mastapy.gears.rating import _324
from mastapy._internal import constructor, conversion
from mastapy.gears.rating.worm import _338
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.face import _411
from mastapy.gears.rating.cylindrical import _418
from mastapy.gears.rating.conical import _498
from mastapy.gears.rating.concept import _508
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4093
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4251
from mastapy._internal.python_net import python_net_import

_GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'GearCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('GearCompoundParametricStudyTool',)


class GearCompoundParametricStudyTool(_4251.MountableComponentCompoundParametricStudyTool):
    '''GearCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _GEAR_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_duty_cycle_results(self) -> '_324.GearDutyCycleRating':
        '''GearDutyCycleRating: 'GearDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _324.GearDutyCycleRating.TYPE not in self.wrapped.GearDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_duty_cycle_results to GearDutyCycleRating. Expected: {}.'.format(self.wrapped.GearDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDutyCycleResults.__class__)(self.wrapped.GearDutyCycleResults) if self.wrapped.GearDutyCycleResults is not None else None

    @property
    def gear_duty_cycle_results_of_type_worm_gear_duty_cycle_rating(self) -> '_338.WormGearDutyCycleRating':
        '''WormGearDutyCycleRating: 'GearDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _338.WormGearDutyCycleRating.TYPE not in self.wrapped.GearDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_duty_cycle_results to WormGearDutyCycleRating. Expected: {}.'.format(self.wrapped.GearDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDutyCycleResults.__class__)(self.wrapped.GearDutyCycleResults) if self.wrapped.GearDutyCycleResults is not None else None

    @property
    def gear_duty_cycle_results_of_type_face_gear_duty_cycle_rating(self) -> '_411.FaceGearDutyCycleRating':
        '''FaceGearDutyCycleRating: 'GearDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _411.FaceGearDutyCycleRating.TYPE not in self.wrapped.GearDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_duty_cycle_results to FaceGearDutyCycleRating. Expected: {}.'.format(self.wrapped.GearDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDutyCycleResults.__class__)(self.wrapped.GearDutyCycleResults) if self.wrapped.GearDutyCycleResults is not None else None

    @property
    def gear_duty_cycle_results_of_type_cylindrical_gear_duty_cycle_rating(self) -> '_418.CylindricalGearDutyCycleRating':
        '''CylindricalGearDutyCycleRating: 'GearDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _418.CylindricalGearDutyCycleRating.TYPE not in self.wrapped.GearDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_duty_cycle_results to CylindricalGearDutyCycleRating. Expected: {}.'.format(self.wrapped.GearDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDutyCycleResults.__class__)(self.wrapped.GearDutyCycleResults) if self.wrapped.GearDutyCycleResults is not None else None

    @property
    def gear_duty_cycle_results_of_type_conical_gear_duty_cycle_rating(self) -> '_498.ConicalGearDutyCycleRating':
        '''ConicalGearDutyCycleRating: 'GearDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _498.ConicalGearDutyCycleRating.TYPE not in self.wrapped.GearDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_duty_cycle_results to ConicalGearDutyCycleRating. Expected: {}.'.format(self.wrapped.GearDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDutyCycleResults.__class__)(self.wrapped.GearDutyCycleResults) if self.wrapped.GearDutyCycleResults is not None else None

    @property
    def gear_duty_cycle_results_of_type_concept_gear_duty_cycle_rating(self) -> '_508.ConceptGearDutyCycleRating':
        '''ConceptGearDutyCycleRating: 'GearDutyCycleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _508.ConceptGearDutyCycleRating.TYPE not in self.wrapped.GearDutyCycleResults.__class__.__mro__:
            raise CastException('Failed to cast gear_duty_cycle_results to ConceptGearDutyCycleRating. Expected: {}.'.format(self.wrapped.GearDutyCycleResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearDutyCycleResults.__class__)(self.wrapped.GearDutyCycleResults) if self.wrapped.GearDutyCycleResults is not None else None

    @property
    def component_analysis_cases(self) -> 'List[_4093.GearParametricStudyTool]':
        '''List[GearParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4093.GearParametricStudyTool))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4093.GearParametricStudyTool]':
        '''List[GearParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4093.GearParametricStudyTool))
        return value
