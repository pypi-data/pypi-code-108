'''_2422.py

CompoundTorsionalSystemDeflectionAnalysis
'''


from mastapy.system_model.analyses_and_results import _2359
from mastapy._internal.python_net import python_net_import

_COMPOUND_TORSIONAL_SYSTEM_DEFLECTION_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'CompoundTorsionalSystemDeflectionAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CompoundTorsionalSystemDeflectionAnalysis',)


class CompoundTorsionalSystemDeflectionAnalysis(_2359.CompoundAnalysis):
    '''CompoundTorsionalSystemDeflectionAnalysis

    This is a mastapy class.
    '''

    TYPE = _COMPOUND_TORSIONAL_SYSTEM_DEFLECTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CompoundTorsionalSystemDeflectionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
