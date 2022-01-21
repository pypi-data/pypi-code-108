'''_4969.py

RigidlyConnectedDesignEntityGroupModalAnalysis
'''


from typing import List

from mastapy.utility.modal_analysis import _1567
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results import _2392
from mastapy._internal.python_net import python_net_import

_RIGIDLY_CONNECTED_DESIGN_ENTITY_GROUP_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'RigidlyConnectedDesignEntityGroupModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidlyConnectedDesignEntityGroupModalAnalysis',)


class RigidlyConnectedDesignEntityGroupModalAnalysis(_2392.DesignEntityGroupAnalysis):
    '''RigidlyConnectedDesignEntityGroupModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _RIGIDLY_CONNECTED_DESIGN_ENTITY_GROUP_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RigidlyConnectedDesignEntityGroupModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def excitation_frequencies_at_reference_speed(self) -> 'List[_1567.DesignEntityExcitationDescription]':
        '''List[DesignEntityExcitationDescription]: 'ExcitationFrequenciesAtReferenceSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ExcitationFrequenciesAtReferenceSpeed, constructor.new(_1567.DesignEntityExcitationDescription))
        return value
