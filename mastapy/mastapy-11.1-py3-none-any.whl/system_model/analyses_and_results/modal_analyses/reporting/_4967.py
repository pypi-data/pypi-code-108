'''_4967.py

RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.modal_analyses.reporting import _4968
from mastapy._internal.python_net import python_net_import

_RIGIDLY_CONNECTED_DESIGN_ENTITY_GROUP_FOR_SINGLE_EXCITATION_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis',)


class RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis(_4968.RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis):
    '''RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _RIGIDLY_CONNECTED_DESIGN_ENTITY_GROUP_FOR_SINGLE_EXCITATION_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RigidlyConnectedDesignEntityGroupForSingleExcitationModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def reference_speed_of_crossing(self) -> 'float':
        '''float: 'ReferenceSpeedOfCrossing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceSpeedOfCrossing
