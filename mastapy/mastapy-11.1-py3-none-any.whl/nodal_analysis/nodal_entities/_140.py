'''_140.py

RigidBar
'''


from mastapy.nodal_analysis.nodal_entities import _136
from mastapy._internal.python_net import python_net_import

_RIGID_BAR = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'RigidBar')


__docformat__ = 'restructuredtext en'
__all__ = ('RigidBar',)


class RigidBar(_136.NodalComponent):
    '''RigidBar

    This is a mastapy class.
    '''

    TYPE = _RIGID_BAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RigidBar.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
