'''_2392.py

DesignEntityGroupAnalysis
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DESIGN_ENTITY_GROUP_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults', 'DesignEntityGroupAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignEntityGroupAnalysis',)


class DesignEntityGroupAnalysis(_0.APIBase):
    '''DesignEntityGroupAnalysis

    This is a mastapy class.
    '''

    TYPE = _DESIGN_ENTITY_GROUP_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignEntityGroupAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
