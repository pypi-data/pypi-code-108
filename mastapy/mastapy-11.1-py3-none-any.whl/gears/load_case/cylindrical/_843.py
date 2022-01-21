'''_843.py

CylindricalGearSetLoadCase
'''


from mastapy.gears.load_case import _834
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Cylindrical', 'CylindricalGearSetLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetLoadCase',)


class CylindricalGearSetLoadCase(_834.GearSetLoadCaseBase):
    '''CylindricalGearSetLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
