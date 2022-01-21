'''_136.py

NodalComponent
'''


from mastapy.nodal_analysis.nodal_entities import _138
from mastapy._internal.python_net import python_net_import

_NODAL_COMPONENT = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'NodalComponent')


__docformat__ = 'restructuredtext en'
__all__ = ('NodalComponent',)


class NodalComponent(_138.NodalEntity):
    '''NodalComponent

    This is a mastapy class.
    '''

    TYPE = _NODAL_COMPONENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodalComponent.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
