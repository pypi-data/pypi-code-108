'''_124.py

BarRigidMBD
'''


from mastapy.nodal_analysis.nodal_entities import _123
from mastapy._internal.python_net import python_net_import

_BAR_RIGID_MBD = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'BarRigidMBD')


__docformat__ = 'restructuredtext en'
__all__ = ('BarRigidMBD',)


class BarRigidMBD(_123.BarMBD):
    '''BarRigidMBD

    This is a mastapy class.
    '''

    TYPE = _BAR_RIGID_MBD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BarRigidMBD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
