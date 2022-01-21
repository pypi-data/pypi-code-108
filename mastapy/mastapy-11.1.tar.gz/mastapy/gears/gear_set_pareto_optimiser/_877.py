'''_877.py

MicroGeometryDesignSpaceSearchCandidate
'''


from mastapy.gears.ltca.cylindrical import _820, _822
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1057
from mastapy.gears.gear_set_pareto_optimiser import _867
from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_DESIGN_SPACE_SEARCH_CANDIDATE = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'MicroGeometryDesignSpaceSearchCandidate')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryDesignSpaceSearchCandidate',)


class MicroGeometryDesignSpaceSearchCandidate(_867.DesignSpaceSearchCandidateBase['_820.CylindricalGearSetLoadDistributionAnalysis', 'MicroGeometryDesignSpaceSearchCandidate']):
    '''MicroGeometryDesignSpaceSearchCandidate

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_DESIGN_SPACE_SEARCH_CANDIDATE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryDesignSpaceSearchCandidate.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def candidate(self) -> '_820.CylindricalGearSetLoadDistributionAnalysis':
        '''CylindricalGearSetLoadDistributionAnalysis: 'Candidate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _820.CylindricalGearSetLoadDistributionAnalysis.TYPE not in self.wrapped.Candidate.__class__.__mro__:
            raise CastException('Failed to cast candidate to CylindricalGearSetLoadDistributionAnalysis. Expected: {}.'.format(self.wrapped.Candidate.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Candidate.__class__)(self.wrapped.Candidate) if self.wrapped.Candidate is not None else None

    @property
    def candidate_for_slider(self) -> '_1057.CylindricalGearSetMicroGeometry':
        '''CylindricalGearSetMicroGeometry: 'CandidateForSlider' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1057.CylindricalGearSetMicroGeometry)(self.wrapped.CandidateForSlider) if self.wrapped.CandidateForSlider is not None else None

    def add_design(self):
        ''' 'AddDesign' is the original name of this method.'''

        self.wrapped.AddDesign()
