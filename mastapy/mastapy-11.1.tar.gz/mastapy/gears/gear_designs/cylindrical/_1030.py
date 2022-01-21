'''_1030.py

StandardRack
'''


from mastapy.gears.gear_designs.cylindrical import _965
from mastapy._internal.python_net import python_net_import

_STANDARD_RACK = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'StandardRack')


__docformat__ = 'restructuredtext en'
__all__ = ('StandardRack',)


class StandardRack(_965.CylindricalGearBasicRack):
    '''StandardRack

    This is a mastapy class.
    '''

    TYPE = _STANDARD_RACK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StandardRack.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
