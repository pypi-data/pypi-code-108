'''_1122.py

ConicalGearProfileModification
'''


from mastapy.gears.micro_geometry import _542
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_PROFILE_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical.MicroGeometry', 'ConicalGearProfileModification')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearProfileModification',)


class ConicalGearProfileModification(_542.ProfileModification):
    '''ConicalGearProfileModification

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_PROFILE_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearProfileModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
