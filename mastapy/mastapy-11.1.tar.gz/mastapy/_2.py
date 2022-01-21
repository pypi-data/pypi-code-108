'''_2.py

LegacyV2RuntimeActivationPolicyAttributeSetter
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_LEGACY_V2_RUNTIME_ACTIVATION_POLICY_ATTRIBUTE_SETTER = python_net_import('SMT.MastaAPI', 'LegacyV2RuntimeActivationPolicyAttributeSetter')


__docformat__ = 'restructuredtext en'
__all__ = ('LegacyV2RuntimeActivationPolicyAttributeSetter',)


class LegacyV2RuntimeActivationPolicyAttributeSetter:
    '''LegacyV2RuntimeActivationPolicyAttributeSetter

    This is a mastapy class.
    '''

    TYPE = _LEGACY_V2_RUNTIME_ACTIVATION_POLICY_ATTRIBUTE_SETTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LegacyV2RuntimeActivationPolicyAttributeSetter.TYPE'):
        self.wrapped = instance_to_wrap

    @staticmethod
    def ensure_config_file_for_current_app_domain_permits_dot_net_2():
        ''' 'EnsureConfigFileForCurrentAppDomainPermitsDotNet2' is the original name of this method.'''

        LegacyV2RuntimeActivationPolicyAttributeSetter.TYPE.EnsureConfigFileForCurrentAppDomainPermitsDotNet2()

    @staticmethod
    def get_config_file_path_for_setup_assembly() -> 'str':
        ''' 'GetConfigFilePathForSetupAssembly' is the original name of this method.

        Returns:
            str
        '''

        method_result = LegacyV2RuntimeActivationPolicyAttributeSetter.TYPE.GetConfigFilePathForSetupAssembly()
        return method_result
