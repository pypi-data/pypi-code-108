'''_144.py

TorsionalFrictionNodePairSimpleLockedStiffness
'''


from mastapy.nodal_analysis.nodal_entities import _143
from mastapy._internal.python_net import python_net_import

_TORSIONAL_FRICTION_NODE_PAIR_SIMPLE_LOCKED_STIFFNESS = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'TorsionalFrictionNodePairSimpleLockedStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('TorsionalFrictionNodePairSimpleLockedStiffness',)


class TorsionalFrictionNodePairSimpleLockedStiffness(_143.TorsionalFrictionNodePair):
    '''TorsionalFrictionNodePairSimpleLockedStiffness

    This is a mastapy class.
    '''

    TYPE = _TORSIONAL_FRICTION_NODE_PAIR_SIMPLE_LOCKED_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorsionalFrictionNodePairSimpleLockedStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
