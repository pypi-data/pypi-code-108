'''_1820.py

RollingBearingFrictionCoefficients
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import
from mastapy.bearings.bearing_results import _1699
from mastapy.bearings.bearing_results.rolling import _1727
from mastapy.utility import _1382

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_ROLLING_BEARING_FRICTION_COEFFICIENTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'RollingBearingFrictionCoefficients')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingBearingFrictionCoefficients',)


class RollingBearingFrictionCoefficients(_1382.IndependentReportablePropertiesBase['RollingBearingFrictionCoefficients']):
    '''RollingBearingFrictionCoefficients

    This is a mastapy class.
    '''

    TYPE = _ROLLING_BEARING_FRICTION_COEFFICIENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingBearingFrictionCoefficients.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_user_specified_f0(self) -> 'bool':
        '''bool: 'UseUserSpecifiedF0' is the original name of this property.'''

        return self.wrapped.UseUserSpecifiedF0

    @use_user_specified_f0.setter
    def use_user_specified_f0(self, value: 'bool'):
        self.wrapped.UseUserSpecifiedF0 = bool(value) if value else False

    @property
    def user_specified_f0(self) -> 'float':
        '''float: 'UserSpecifiedF0' is the original name of this property.'''

        return self.wrapped.UserSpecifiedF0

    @user_specified_f0.setter
    def user_specified_f0(self, value: 'float'):
        self.wrapped.UserSpecifiedF0 = float(value) if value else 0.0

    @property
    def use_user_specified_f1_for_din732(self) -> 'bool':
        '''bool: 'UseUserSpecifiedF1ForDIN732' is the original name of this property.'''

        return self.wrapped.UseUserSpecifiedF1ForDIN732

    @use_user_specified_f1_for_din732.setter
    def use_user_specified_f1_for_din732(self, value: 'bool'):
        self.wrapped.UseUserSpecifiedF1ForDIN732 = bool(value) if value else False

    @property
    def user_specified_f1_for_din732(self) -> 'float':
        '''float: 'UserSpecifiedF1ForDIN732' is the original name of this property.'''

        return self.wrapped.UserSpecifiedF1ForDIN732

    @user_specified_f1_for_din732.setter
    def user_specified_f1_for_din732(self, value: 'float'):
        self.wrapped.UserSpecifiedF1ForDIN732 = float(value) if value else 0.0

    @property
    def use_user_specified_f0r(self) -> 'bool':
        '''bool: 'UseUserSpecifiedF0r' is the original name of this property.'''

        return self.wrapped.UseUserSpecifiedF0r

    @use_user_specified_f0r.setter
    def use_user_specified_f0r(self, value: 'bool'):
        self.wrapped.UseUserSpecifiedF0r = bool(value) if value else False

    @property
    def user_specified_f0r(self) -> 'float':
        '''float: 'UserSpecifiedF0r' is the original name of this property.'''

        return self.wrapped.UserSpecifiedF0r

    @user_specified_f0r.setter
    def user_specified_f0r(self, value: 'float'):
        self.wrapped.UserSpecifiedF0r = float(value) if value else 0.0

    @property
    def use_user_specified_f1r(self) -> 'bool':
        '''bool: 'UseUserSpecifiedF1r' is the original name of this property.'''

        return self.wrapped.UseUserSpecifiedF1r

    @use_user_specified_f1r.setter
    def use_user_specified_f1r(self, value: 'bool'):
        self.wrapped.UseUserSpecifiedF1r = bool(value) if value else False

    @property
    def user_specified_f1r(self) -> 'float':
        '''float: 'UserSpecifiedF1r' is the original name of this property.'''

        return self.wrapped.UserSpecifiedF1r

    @user_specified_f1r.setter
    def user_specified_f1r(self, value: 'float'):
        self.wrapped.UserSpecifiedF1r = float(value) if value else 0.0

    @property
    def iso14179_settings_database(self) -> 'str':
        '''str: 'ISO14179SettingsDatabase' is the original name of this property.'''

        return self.wrapped.ISO14179SettingsDatabase.SelectedItemName

    @iso14179_settings_database.setter
    def iso14179_settings_database(self, value: 'str'):
        self.wrapped.ISO14179SettingsDatabase.SetSelectedItem(str(value) if value else '')

    @property
    def iso14179_static_equivalent_load_factors(self) -> '_1699.EquivalentLoadFactors':
        '''EquivalentLoadFactors: 'ISO14179StaticEquivalentLoadFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1699.EquivalentLoadFactors)(self.wrapped.ISO14179StaticEquivalentLoadFactors) if self.wrapped.ISO14179StaticEquivalentLoadFactors is not None else None

    @property
    def iso14179_dynamic_equivalent_load_factors(self) -> '_1699.EquivalentLoadFactors':
        '''EquivalentLoadFactors: 'ISO14179DynamicEquivalentLoadFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1699.EquivalentLoadFactors)(self.wrapped.ISO14179DynamicEquivalentLoadFactors) if self.wrapped.ISO14179DynamicEquivalentLoadFactors is not None else None

    @property
    def iso14179_settings(self) -> '_1727.ISO14179Settings':
        '''ISO14179Settings: 'ISO14179Settings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1727.ISO14179Settings)(self.wrapped.ISO14179Settings) if self.wrapped.ISO14179Settings is not None else None
