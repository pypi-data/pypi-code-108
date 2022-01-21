'''_115.py

ElementScalarState
'''


from mastapy.nodal_analysis.states import _116
from mastapy._internal.python_net import python_net_import

_ELEMENT_SCALAR_STATE = python_net_import('SMT.MastaAPI.NodalAnalysis.States', 'ElementScalarState')


__docformat__ = 'restructuredtext en'
__all__ = ('ElementScalarState',)


class ElementScalarState(_116.ElementVectorState):
    '''ElementScalarState

    This is a mastapy class.
    '''

    TYPE = _ELEMENT_SCALAR_STATE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElementScalarState.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
