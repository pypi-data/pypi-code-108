'''_4971.py

SingleExcitationResultsModalAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.reporting import _4967, _4964
from mastapy._internal.python_net import python_net_import

_SINGLE_EXCITATION_RESULTS_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'SingleExcitationResultsModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SingleExcitationResultsModalAnalysis',)


class SingleExcitationResultsModalAnalysis(_4964.DesignEntityModalAnalysisGroupResults):
    '''SingleExcitationResultsModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _SINGLE_EXCITATION_RESULTS_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingleExcitationResultsModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def harmonic_index(self) -> 'int':
        '''int: 'HarmonicIndex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HarmonicIndex

    @property
    def all_rigidly_connected_groups(self) -> 'List[_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]: 'AllRigidlyConnectedGroups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AllRigidlyConnectedGroups, constructor.new(_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis))
        return value

    @property
    def rigidly_connected_groups_with_significant_energy(self) -> 'List[_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]: 'RigidlyConnectedGroupsWithSignificantEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidlyConnectedGroupsWithSignificantEnergy, constructor.new(_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis))
        return value

    @property
    def rigidly_connected_groups_with_significant_kinetic_energy(self) -> 'List[_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]: 'RigidlyConnectedGroupsWithSignificantKineticEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidlyConnectedGroupsWithSignificantKineticEnergy, constructor.new(_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis))
        return value

    @property
    def rigidly_connected_groups_with_significant_strain_energy(self) -> 'List[_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis]: 'RigidlyConnectedGroupsWithSignificantStrainEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidlyConnectedGroupsWithSignificantStrainEnergy, constructor.new(_4967.RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis))
        return value
