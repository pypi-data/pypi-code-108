'''_127.py

ComponentNodalComposite
'''


from mastapy.nodal_analysis.nodal_entities import _137
from mastapy._internal.python_net import python_net_import

_COMPONENT_NODAL_COMPOSITE = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'ComponentNodalComposite')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentNodalComposite',)


class ComponentNodalComposite(_137.NodalComposite):
    '''ComponentNodalComposite

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_NODAL_COMPOSITE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentNodalComposite.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
