'''_839.py

FaceGearLoadCase
'''


from mastapy.gears.load_case import _833
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Face', 'FaceGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearLoadCase',)


class FaceGearLoadCase(_833.GearLoadCaseBase):
    '''FaceGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
