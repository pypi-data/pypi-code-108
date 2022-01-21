'''_1014.py

LTCALoadCaseModifiableSettings
'''


from mastapy._internal import constructor
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_LTCA_LOAD_CASE_MODIFIABLE_SETTINGS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'LTCALoadCaseModifiableSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('LTCALoadCaseModifiableSettings',)


class LTCALoadCaseModifiableSettings(_1382.IndependentReportablePropertiesBase['LTCALoadCaseModifiableSettings']):
    '''LTCALoadCaseModifiableSettings

    This is a mastapy class.
    '''

    TYPE = _LTCA_LOAD_CASE_MODIFIABLE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LTCALoadCaseModifiableSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def apply_application_and_dynamic_factor(self) -> 'bool':
        '''bool: 'ApplyApplicationAndDynamicFactor' is the original name of this property.'''

        return self.wrapped.ApplyApplicationAndDynamicFactor

    @apply_application_and_dynamic_factor.setter
    def apply_application_and_dynamic_factor(self, value: 'bool'):
        self.wrapped.ApplyApplicationAndDynamicFactor = bool(value) if value else False

    @property
    def include_change_in_contact_point_due_to_micro_geometry(self) -> 'bool':
        '''bool: 'IncludeChangeInContactPointDueToMicroGeometry' is the original name of this property.'''

        return self.wrapped.IncludeChangeInContactPointDueToMicroGeometry

    @include_change_in_contact_point_due_to_micro_geometry.setter
    def include_change_in_contact_point_due_to_micro_geometry(self, value: 'bool'):
        self.wrapped.IncludeChangeInContactPointDueToMicroGeometry = bool(value) if value else False

    @property
    def use_jacobian_advanced_ltca_solver(self) -> 'bool':
        '''bool: 'UseJacobianAdvancedLTCASolver' is the original name of this property.'''

        return self.wrapped.UseJacobianAdvancedLTCASolver

    @use_jacobian_advanced_ltca_solver.setter
    def use_jacobian_advanced_ltca_solver(self, value: 'bool'):
        self.wrapped.UseJacobianAdvancedLTCASolver = bool(value) if value else False
