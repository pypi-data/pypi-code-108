'''_814.py

CylindricalGearContactStiffnessNode
'''


from mastapy.gears.ltca import _796
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_CONTACT_STIFFNESS_NODE = python_net_import('SMT.MastaAPI.Gears.LTCA.Cylindrical', 'CylindricalGearContactStiffnessNode')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearContactStiffnessNode',)


class CylindricalGearContactStiffnessNode(_796.GearContactStiffnessNode):
    '''CylindricalGearContactStiffnessNode

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_CONTACT_STIFFNESS_NODE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearContactStiffnessNode.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
