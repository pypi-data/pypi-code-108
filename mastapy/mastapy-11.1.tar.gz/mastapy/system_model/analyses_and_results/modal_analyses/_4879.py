'''_4879.py

FrequencyResponseAnalysisOptions
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.analyses_and_results.analysis_cases import _7253
from mastapy.system_model.analyses_and_results.static_loads import _6518
from mastapy._internal.python_net import python_net_import

_FREQUENCY_RESPONSE_ANALYSIS_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'FrequencyResponseAnalysisOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('FrequencyResponseAnalysisOptions',)


class FrequencyResponseAnalysisOptions(_7253.AbstractAnalysisOptions['_6518.LoadCase']):
    '''FrequencyResponseAnalysisOptions

    This is a mastapy class.
    '''

    TYPE = _FREQUENCY_RESPONSE_ANALYSIS_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FrequencyResponseAnalysisOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_shaft_harmonics(self) -> 'int':
        '''int: 'NumberOfShaftHarmonics' is the original name of this property.'''

        return self.wrapped.NumberOfShaftHarmonics

    @number_of_shaft_harmonics.setter
    def number_of_shaft_harmonics(self, value: 'int'):
        self.wrapped.NumberOfShaftHarmonics = int(value) if value else 0

    @property
    def number_of_gear_mesh_harmonics(self) -> 'int':
        '''int: 'NumberOfGearMeshHarmonics' is the original name of this property.'''

        return self.wrapped.NumberOfGearMeshHarmonics

    @number_of_gear_mesh_harmonics.setter
    def number_of_gear_mesh_harmonics(self, value: 'int'):
        self.wrapped.NumberOfGearMeshHarmonics = int(value) if value else 0

    @property
    def number_of_input_shaft_harmonics(self) -> 'int':
        '''int: 'NumberOfInputShaftHarmonics' is the original name of this property.'''

        return self.wrapped.NumberOfInputShaftHarmonics

    @number_of_input_shaft_harmonics.setter
    def number_of_input_shaft_harmonics(self, value: 'int'):
        self.wrapped.NumberOfInputShaftHarmonics = int(value) if value else 0

    @property
    def threshold_for_significant_kinetic_energy(self) -> 'float':
        '''float: 'ThresholdForSignificantKineticEnergy' is the original name of this property.'''

        return self.wrapped.ThresholdForSignificantKineticEnergy

    @threshold_for_significant_kinetic_energy.setter
    def threshold_for_significant_kinetic_energy(self, value: 'float'):
        self.wrapped.ThresholdForSignificantKineticEnergy = float(value) if value else 0.0

    @property
    def threshold_for_significant_strain_energy(self) -> 'float':
        '''float: 'ThresholdForSignificantStrainEnergy' is the original name of this property.'''

        return self.wrapped.ThresholdForSignificantStrainEnergy

    @threshold_for_significant_strain_energy.setter
    def threshold_for_significant_strain_energy(self, value: 'float'):
        self.wrapped.ThresholdForSignificantStrainEnergy = float(value) if value else 0.0

    @property
    def reference_power_load(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'ReferencePowerLoad' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.ReferencePowerLoad) if self.wrapped.ReferencePowerLoad is not None else None

    @reference_power_load.setter
    def reference_power_load(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.ReferencePowerLoad = value
