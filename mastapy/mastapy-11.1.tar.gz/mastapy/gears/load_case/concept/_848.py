'''_848.py

ConceptGearLoadCase
'''


from mastapy.gears.load_case import _833
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Concept', 'ConceptGearLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearLoadCase',)


class ConceptGearLoadCase(_833.GearLoadCaseBase):
    '''ConceptGearLoadCase

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
