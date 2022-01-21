'''_7253.py

AbstractAnalysisOptions
'''


from typing import Generic, TypeVar

from mastapy import _0
from mastapy.system_model.analyses_and_results.static_loads import _6518
from mastapy._internal.python_net import python_net_import

_ABSTRACT_ANALYSIS_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'AbstractAnalysisOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractAnalysisOptions',)


T = TypeVar('T', bound='_6518.LoadCase')


class AbstractAnalysisOptions(_0.APIBase, Generic[T]):
    '''AbstractAnalysisOptions

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _ABSTRACT_ANALYSIS_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractAnalysisOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
