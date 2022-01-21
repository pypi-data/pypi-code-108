'''_1595.py

DatabaseSettings
'''


from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_DATABASE_SETTINGS = python_net_import('SMT.MastaAPI.Utility.Databases', 'DatabaseSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('DatabaseSettings',)


class DatabaseSettings(_1387.PerMachineSettings):
    '''DatabaseSettings

    This is a mastapy class.
    '''

    TYPE = _DATABASE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatabaseSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
