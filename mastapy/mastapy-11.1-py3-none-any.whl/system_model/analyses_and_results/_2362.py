'''_2362.py

AdvancedSystemDeflectionSubAnalysis
'''


from mastapy.system_model.analyses_and_results import _2360
from mastapy._internal.python_net import python_net_import

_ADVANCED_SYSTEM_DEFLECTION_SUB_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'AdvancedSystemDeflectionSubAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedSystemDeflectionSubAnalysis',)


class AdvancedSystemDeflectionSubAnalysis(_2360.SingleAnalysis):
    '''AdvancedSystemDeflectionSubAnalysis

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_SYSTEM_DEFLECTION_SUB_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedSystemDeflectionSubAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
