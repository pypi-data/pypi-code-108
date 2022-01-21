'''_871.py

GearSetOptimiserCandidate
'''


from mastapy.gears.rating import _321, _328, _329
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.zerol_bevel import _337
from mastapy.gears.rating.worm import _341, _342
from mastapy.gears.rating.straight_bevel_diff import _363
from mastapy.gears.rating.straight_bevel import _367
from mastapy.gears.rating.spiral_bevel import _370
from mastapy.gears.rating.klingelnberg_spiral_bevel import _373
from mastapy.gears.rating.klingelnberg_hypoid import _376
from mastapy.gears.rating.klingelnberg_conical import _379
from mastapy.gears.rating.hypoid import _406
from mastapy.gears.rating.face import _415, _416
from mastapy.gears.rating.cylindrical import _427, _428
from mastapy.gears.rating.conical import _501, _502
from mastapy.gears.rating.concept import _512, _513
from mastapy.gears.rating.bevel import _516
from mastapy.gears.rating.agma_gleason_conical import _527
from mastapy.gears.gear_set_pareto_optimiser import _867
from mastapy._internal.python_net import python_net_import

_GEAR_SET_OPTIMISER_CANDIDATE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'GearSetOptimiserCandidate')


__docformat__ = 'restructuredtext en'
__all__ = ('GearSetOptimiserCandidate',)


class GearSetOptimiserCandidate(_867.DesignSpaceSearchCandidateBase['_321.AbstractGearSetRating', 'GearSetOptimiserCandidate']):
    '''GearSetOptimiserCandidate

    This is a mastapy class.
    '''

    TYPE = _GEAR_SET_OPTIMISER_CANDIDATE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearSetOptimiserCandidate.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def candidate(self) -> '_321.AbstractGearSetRating':
        '''AbstractGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _321.AbstractGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to AbstractGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_gear_set_duty_cycle_rating(self) -> '_328.GearSetDutyCycleRating':
        '''GearSetDutyCycleRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _328.GearSetDutyCycleRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to GearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_gear_set_rating(self) -> '_329.GearSetRating':
        '''GearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _329.GearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to GearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_zerol_bevel_gear_set_rating(self) -> '_337.ZerolBevelGearSetRating':
        '''ZerolBevelGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _337.ZerolBevelGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to ZerolBevelGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_worm_gear_set_duty_cycle_rating(self) -> '_341.WormGearSetDutyCycleRating':
        '''WormGearSetDutyCycleRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _341.WormGearSetDutyCycleRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to WormGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_worm_gear_set_rating(self) -> '_342.WormGearSetRating':
        '''WormGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _342.WormGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to WormGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_straight_bevel_diff_gear_set_rating(self) -> '_363.StraightBevelDiffGearSetRating':
        '''StraightBevelDiffGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _363.StraightBevelDiffGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to StraightBevelDiffGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_straight_bevel_gear_set_rating(self) -> '_367.StraightBevelGearSetRating':
        '''StraightBevelGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _367.StraightBevelGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to StraightBevelGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_spiral_bevel_gear_set_rating(self) -> '_370.SpiralBevelGearSetRating':
        '''SpiralBevelGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _370.SpiralBevelGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to SpiralBevelGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(self) -> '_373.KlingelnbergCycloPalloidSpiralBevelGearSetRating':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _373.KlingelnbergCycloPalloidSpiralBevelGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to KlingelnbergCycloPalloidSpiralBevelGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set_rating(self) -> '_376.KlingelnbergCycloPalloidHypoidGearSetRating':
        '''KlingelnbergCycloPalloidHypoidGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _376.KlingelnbergCycloPalloidHypoidGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to KlingelnbergCycloPalloidHypoidGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_klingelnberg_cyclo_palloid_conical_gear_set_rating(self) -> '_379.KlingelnbergCycloPalloidConicalGearSetRating':
        '''KlingelnbergCycloPalloidConicalGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _379.KlingelnbergCycloPalloidConicalGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to KlingelnbergCycloPalloidConicalGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_hypoid_gear_set_rating(self) -> '_406.HypoidGearSetRating':
        '''HypoidGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _406.HypoidGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to HypoidGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_face_gear_set_duty_cycle_rating(self) -> '_415.FaceGearSetDutyCycleRating':
        '''FaceGearSetDutyCycleRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _415.FaceGearSetDutyCycleRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to FaceGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_face_gear_set_rating(self) -> '_416.FaceGearSetRating':
        '''FaceGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _416.FaceGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to FaceGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_cylindrical_gear_set_duty_cycle_rating(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _427.CylindricalGearSetDutyCycleRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to CylindricalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_cylindrical_gear_set_rating(self) -> '_428.CylindricalGearSetRating':
        '''CylindricalGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _428.CylindricalGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to CylindricalGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_conical_gear_set_duty_cycle_rating(self) -> '_501.ConicalGearSetDutyCycleRating':
        '''ConicalGearSetDutyCycleRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _501.ConicalGearSetDutyCycleRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to ConicalGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_conical_gear_set_rating(self) -> '_502.ConicalGearSetRating':
        '''ConicalGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _502.ConicalGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to ConicalGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_concept_gear_set_duty_cycle_rating(self) -> '_512.ConceptGearSetDutyCycleRating':
        '''ConceptGearSetDutyCycleRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _512.ConceptGearSetDutyCycleRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to ConceptGearSetDutyCycleRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_concept_gear_set_rating(self) -> '_513.ConceptGearSetRating':
        '''ConceptGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _513.ConceptGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to ConceptGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_bevel_gear_set_rating(self) -> '_516.BevelGearSetRating':
        '''BevelGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _516.BevelGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to BevelGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_of_type_agma_gleason_conical_gear_set_rating(self) -> '_527.AGMAGleasonConicalGearSetRating':
        '''AGMAGleasonConicalGearSetRating: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _527.AGMAGleasonConicalGearSetRating.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to AGMAGleasonConicalGearSetRating. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    def add_design(self):
        ''' 'AddDesign' is the original name of this method.'''

        self.wrapped.AddDesign()
