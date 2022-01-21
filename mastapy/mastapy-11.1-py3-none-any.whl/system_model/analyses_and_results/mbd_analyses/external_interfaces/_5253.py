'''_5253.py

DynamicExternalInterfaceOptions
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5173
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DYNAMIC_EXTERNAL_INTERFACE_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.ExternalInterfaces', 'DynamicExternalInterfaceOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicExternalInterfaceOptions',)


class DynamicExternalInterfaceOptions(_0.APIBase):
    '''DynamicExternalInterfaceOptions

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_EXTERNAL_INTERFACE_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicExternalInterfaceOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sample_time(self) -> 'float':
        '''float: 'SampleTime' is the original name of this property.'''

        return self.wrapped.SampleTime

    @sample_time.setter
    def sample_time(self, value: 'float'):
        self.wrapped.SampleTime = float(value) if value else 0.0

    @property
    def generate_load_case(self) -> 'bool':
        '''bool: 'GenerateLoadCase' is the original name of this property.'''

        return self.wrapped.GenerateLoadCase

    @generate_load_case.setter
    def generate_load_case(self, value: 'bool'):
        self.wrapped.GenerateLoadCase = bool(value) if value else False

    @property
    def save_results(self) -> 'bool':
        '''bool: 'SaveResults' is the original name of this property.'''

        return self.wrapped.SaveResults

    @save_results.setter
    def save_results(self, value: 'bool'):
        self.wrapped.SaveResults = bool(value) if value else False

    @property
    def input_signal_filter_level(self) -> '_5173.InputSignalFilterLevel':
        '''InputSignalFilterLevel: 'InputSignalFilterLevel' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.InputSignalFilterLevel)
        return constructor.new(_5173.InputSignalFilterLevel)(value) if value is not None else None

    @input_signal_filter_level.setter
    def input_signal_filter_level(self, value: '_5173.InputSignalFilterLevel'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.InputSignalFilterLevel = value

    @property
    def path_of_saved_file(self) -> 'str':
        '''str: 'PathOfSavedFile' is the original name of this property.'''

        return self.wrapped.PathOfSavedFile

    @path_of_saved_file.setter
    def path_of_saved_file(self, value: 'str'):
        self.wrapped.PathOfSavedFile = str(value) if value else ''
