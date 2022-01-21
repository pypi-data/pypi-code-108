'''_840.py

FaceGearSetLoadCase
'''


from mastapy.gears.load_case import _834
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_SET_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Face', 'FaceGearSetLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetLoadCase',)


class FaceGearSetLoadCase(_834.GearSetLoadCaseBase):
    '''FaceGearSetLoadCase

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
