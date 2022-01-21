'''_145.py

TwoBodyConnectionNodalComponent
'''


from mastapy.nodal_analysis.nodal_entities import _127
from mastapy._internal.python_net import python_net_import

_TWO_BODY_CONNECTION_NODAL_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'TwoBodyConnectionNodalComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('TwoBodyConnectionNodalComponent',)


class TwoBodyConnectionNodalComponent(_127.ComponentNodalComposite):
    '''TwoBodyConnectionNodalComponent

    This is a mastapy class.
    '''

    TYPE = _TWO_BODY_CONNECTION_NODAL_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TwoBodyConnectionNodalComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
