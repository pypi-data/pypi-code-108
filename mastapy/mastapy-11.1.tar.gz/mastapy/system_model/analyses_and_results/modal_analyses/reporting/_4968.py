'''_4968.py

RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.reporting import _4963
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RIGIDLY_CONNECTED_DESIGN_ENTITY_GROUP_FOR_SINGLE_MODE_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Reporting', 'RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis',)


class RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis(_0.APIBase):
    '''RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _RIGIDLY_CONNECTED_DESIGN_ENTITY_GROUP_FOR_SINGLE_MODE_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RigidlyConnectedDesignEntityGroupForSingleModeModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def percentage_kinetic_energy(self) -> 'float':
        '''float: 'PercentageKineticEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageKineticEnergy

    @property
    def percentage_strain_energy(self) -> 'float':
        '''float: 'PercentageStrainEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageStrainEnergy

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def shaft_names(self) -> 'str':
        '''str: 'ShaftNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftNames

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
    def component_results(self) -> 'List[_4963.ComponentPerModeResult]':
        '''List[ComponentPerModeResult]: 'ComponentResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentResults, constructor.new(_4963.ComponentPerModeResult))
        return value
