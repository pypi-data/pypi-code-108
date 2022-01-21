'''_64.py

FEUserSettings
'''


from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_FE_USER_SETTINGS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'FEUserSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('FEUserSettings',)


class FEUserSettings(_1387.PerMachineSettings):
    '''FEUserSettings

    This is a mastapy class.
    '''

    TYPE = _FE_USER_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEUserSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
