'''_2389.py

ConnectionAnalysis
'''


from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results import _2393
from mastapy._internal.python_net import python_net_import

_CONNECTION_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'ConnectionAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectionAnalysis',)


class ConnectionAnalysis(_2393.DesignEntitySingleContextAnalysis):
    '''ConnectionAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONNECTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def short_name(self) -> 'str':
        '''str: 'ShortName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShortName
