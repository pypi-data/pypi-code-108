'''_107.py

SingularDegreeOfFreedomAnalysis
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SINGULAR_DEGREE_OF_FREEDOM_ANALYSIS = python_net_import('SMT.MastaAPI.NodalAnalysis.SystemSolvers', 'SingularDegreeOfFreedomAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SingularDegreeOfFreedomAnalysis',)


class SingularDegreeOfFreedomAnalysis(_0.APIBase):
    '''SingularDegreeOfFreedomAnalysis

    This is a mastapy class.
    '''

    TYPE = _SINGULAR_DEGREE_OF_FREEDOM_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingularDegreeOfFreedomAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def vector_value(self) -> 'float':
        '''float: 'VectorValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VectorValue

    @property
    def global_degree_of_freedom(self) -> 'int':
        '''int: 'GlobalDegreeOfFreedom' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GlobalDegreeOfFreedom

    @property
    def node_id(self) -> 'int':
        '''int: 'NodeID' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NodeID

    @property
    def node_degree_of_freedom(self) -> 'int':
        '''int: 'NodeDegreeOfFreedom' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NodeDegreeOfFreedom

    @property
    def components_using_node(self) -> 'str':
        '''str: 'ComponentsUsingNode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ComponentsUsingNode

    @property
    def nodal_entities_using_node(self) -> 'str':
        '''str: 'NodalEntitiesUsingNode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NodalEntitiesUsingNode

    @property
    def node_names(self) -> 'str':
        '''str: 'NodeNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NodeNames
