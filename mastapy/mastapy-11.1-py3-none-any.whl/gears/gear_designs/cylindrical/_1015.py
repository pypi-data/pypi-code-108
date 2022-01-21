'''_1015.py

LtcaSettings
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _1014
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_LTCA_SETTINGS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'LtcaSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('LtcaSettings',)


class LtcaSettings(_1382.IndependentReportablePropertiesBase['LtcaSettings']):
    '''LtcaSettings

    This is a mastapy class.
    '''

    TYPE = _LTCA_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LtcaSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def include_extended_tip_contact(self) -> 'bool':
        '''bool: 'IncludeExtendedTipContact' is the original name of this property.'''

        return self.wrapped.IncludeExtendedTipContact

    @include_extended_tip_contact.setter
    def include_extended_tip_contact(self, value: 'bool'):
        self.wrapped.IncludeExtendedTipContact = bool(value) if value else False

    @property
    def face_utilization_load_cutoff_parameter(self) -> 'float':
        '''float: 'FaceUtilizationLoadCutoffParameter' is the original name of this property.'''

        return self.wrapped.FaceUtilizationLoadCutoffParameter

    @face_utilization_load_cutoff_parameter.setter
    def face_utilization_load_cutoff_parameter(self, value: 'float'):
        self.wrapped.FaceUtilizationLoadCutoffParameter = float(value) if value else 0.0

    @property
    def load_case_modifiable_settings(self) -> '_1014.LTCALoadCaseModifiableSettings':
        '''LTCALoadCaseModifiableSettings: 'LoadCaseModifiableSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1014.LTCALoadCaseModifiableSettings)(self.wrapped.LoadCaseModifiableSettings) if self.wrapped.LoadCaseModifiableSettings is not None else None
