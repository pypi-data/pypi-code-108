'''_825.py

ConicalGearContactStiffness
'''


from mastapy.gears.ltca import _795
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_CONTACT_STIFFNESS = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalGearContactStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearContactStiffness',)


class ConicalGearContactStiffness(_795.GearContactStiffness):
    '''ConicalGearContactStiffness

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_CONTACT_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearContactStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
