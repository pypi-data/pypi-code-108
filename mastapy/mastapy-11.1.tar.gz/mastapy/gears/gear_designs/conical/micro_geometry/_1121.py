'''_1121.py

ConicalGearLeadModification
'''


from mastapy.gears.micro_geometry import _532
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_LEAD_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical.MicroGeometry', 'ConicalGearLeadModification')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearLeadModification',)


class ConicalGearLeadModification(_532.LeadModification):
    '''ConicalGearLeadModification

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_LEAD_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearLeadModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
