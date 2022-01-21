'''_826.py

ConicalGearContactStiffnessNode
'''


from mastapy.gears.ltca import _796
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_CONTACT_STIFFNESS_NODE = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalGearContactStiffnessNode')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearContactStiffnessNode',)


class ConicalGearContactStiffnessNode(_796.GearContactStiffnessNode):
    '''ConicalGearContactStiffnessNode

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_CONTACT_STIFFNESS_NODE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearContactStiffnessNode.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
