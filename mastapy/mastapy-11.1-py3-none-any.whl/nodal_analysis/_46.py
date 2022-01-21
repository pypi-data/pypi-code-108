'''_46.py

AnalysisSettingsDatabase
'''


from mastapy.utility.databases import _1596
from mastapy.nodal_analysis import _47
from mastapy._internal.python_net import python_net_import

_ANALYSIS_SETTINGS_DATABASE = python_net_import('SMT.MastaAPI.NodalAnalysis', 'AnalysisSettingsDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('AnalysisSettingsDatabase',)


class AnalysisSettingsDatabase(_1596.NamedDatabase['_47.AnalysisSettingsObjects']):
    '''AnalysisSettingsDatabase

    This is a mastapy class.
    '''

    TYPE = _ANALYSIS_SETTINGS_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AnalysisSettingsDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
