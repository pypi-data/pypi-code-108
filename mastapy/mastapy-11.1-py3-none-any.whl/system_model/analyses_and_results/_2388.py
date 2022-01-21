'''_2388.py

AnalysisCaseVariable
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ANALYSIS_CASE_VARIABLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'AnalysisCaseVariable')


__docformat__ = 'restructuredtext en'
__all__ = ('AnalysisCaseVariable',)


class AnalysisCaseVariable(_0.APIBase):
    '''AnalysisCaseVariable

    This is a mastapy class.
    '''

    TYPE = _ANALYSIS_CASE_VARIABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AnalysisCaseVariable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def entity_name(self) -> 'str':
        '''str: 'EntityName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntityName
