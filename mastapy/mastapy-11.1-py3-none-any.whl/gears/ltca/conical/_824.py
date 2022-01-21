'''_824.py

ConicalGearBendingStiffnessNode
'''


from mastapy.gears.ltca import _794
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_BENDING_STIFFNESS_NODE = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalGearBendingStiffnessNode')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearBendingStiffnessNode',)


class ConicalGearBendingStiffnessNode(_794.GearBendingStiffnessNode):
    '''ConicalGearBendingStiffnessNode

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_BENDING_STIFFNESS_NODE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearBendingStiffnessNode.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
