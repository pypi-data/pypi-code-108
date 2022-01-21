'''_116.py

ElementVectorState
'''


from mastapy.nodal_analysis.states import _117
from mastapy._internal.python_net import python_net_import

_ELEMENT_VECTOR_STATE = python_net_import('SMT.MastaAPI.NodalAnalysis.States', 'ElementVectorState')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementVectorState',)


class ElementVectorState(_117.EntityVectorState):
    '''ElementVectorState

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_VECTOR_STATE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementVectorState.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
