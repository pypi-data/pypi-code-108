'''_4972.py

SingleModeResults
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.reporting import _4968, _4964
from mastapy._internal.python_net import python_net_import

_SINGLE_MODE_RESULTS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'SingleModeResults')


__docformat__ = 'restructuredtext en'
__all__ = ('SingleModeResults',)


class SingleModeResults(_4964.DesignEntityModalAnalysisGroupResults):
    '''SingleModeResults

    This is a mastapy class.
    '''

    TYPE = _SINGLE_MODE_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingleModeResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mode_id(self) -> 'int':
        '''int: 'ModeID' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModeID

    @property
    def mode_frequency(self) -> 'float':
        '''float: 'ModeFrequency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModeFrequency

    @property
    def all_rigidly_connected_groups(self) -> 'List[_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]: 'AllRigidlyConnectedGroups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AllRigidlyConnectedGroups, constructor.new(_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis))
        return value

    @property
    def rigidly_connected_groups_with_significant_energy(self) -> 'List[_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]: 'RigidlyConnectedGroupsWithSignificantEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidlyConnectedGroupsWithSignificantEnergy, constructor.new(_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis))
        return value

    @property
    def rigidly_connected_groups_with_significant_kinetic_energy(self) -> 'List[_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]: 'RigidlyConnectedGroupsWithSignificantKineticEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidlyConnectedGroupsWithSignificantKineticEnergy, constructor.new(_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis))
        return value

    @property
    def rigidly_connected_groups_with_significant_strain_energy(self) -> 'List[_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]':
        '''List[RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis]: 'RigidlyConnectedGroupsWithSignificantStrainEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidlyConnectedGroupsWithSignificantStrainEnergy, constructor.new(_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis))
        return value
