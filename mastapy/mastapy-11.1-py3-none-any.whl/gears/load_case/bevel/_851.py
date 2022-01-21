'''_851.py

BevelLoadCase
'''


from mastapy.gears.load_case.conical import _845
from mastapy._internal.python_net import python_net_import

_BEVEL_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Bevel', 'BevelLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelLoadCase',)


class BevelLoadCase(_845.ConicalGearLoadCase):
    '''BevelLoadCase

    This is a mastapy class.
    '''

    TYPE = _BEVEL_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
