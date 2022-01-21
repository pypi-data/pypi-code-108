'''_128.py

ConcentricConnectionNodalComponent
'''


from mastapy.nodal_analysis.nodal_entities import _145
from mastapy._internal.python_net import python_net_import

_CONCENTRIC_CONNECTION_NODAL_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'ConcentricConnectionNodalComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('ConcentricConnectionNodalComponent',)


class ConcentricConnectionNodalComponent(_145.TwoBodyConnectionNodalComponent):
    '''ConcentricConnectionNodalComponent

    This is a mastapy class.
    '''

    TYPE = _CONCENTRIC_CONNECTION_NODAL_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConcentricConnectionNodalComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
