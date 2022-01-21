'''_845.py

ConicalGearLoadCase
'''


from mastapy.gears.load_case import _833
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Conical', 'ConicalGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearLoadCase',)


class ConicalGearLoadCase(_833.GearLoadCaseBase):
    '''ConicalGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
