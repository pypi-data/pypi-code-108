'''_836.py

WormGearLoadCase
'''


from mastapy.gears.load_case import _833
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Worm', 'WormGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearLoadCase',)


class WormGearLoadCase(_833.GearLoadCaseBase):
    '''WormGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
