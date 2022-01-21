'''_1600.py

CADExportSettings
'''


from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_CAD_EXPORT_SETTINGS = python_net_import('SMT.MastaAPI.Utility.CadExport', 'CADExportSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CADExportSettings',)


class CADExportSettings(_1387.PerMachineSettings):
    '''CADExportSettings

    This is a mastapy class.
    '''

    TYPE = _CAD_EXPORT_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CADExportSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
