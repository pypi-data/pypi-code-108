'''_1382.py

IndependentReportablePropertiesBase
'''


from typing import Generic, TypeVar

from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INDEPENDENT_REPORTABLE_PROPERTIES_BASE = python_net_import('SMT.MastaAPI.Utility', 'IndependentReportablePropertiesBase')


__docformat__ = 'restructuredtext en'
__all__ = ('IndependentReportablePropertiesBase',)


T = TypeVar('T', bound='IndependentReportablePropertiesBase')


class IndependentReportablePropertiesBase(_0.APIBase, Generic[T]):
    '''IndependentReportablePropertiesBase

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _INDEPENDENT_REPORTABLE_PROPERTIES_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'IndependentReportablePropertiesBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
