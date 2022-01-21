'''_512.py

ConceptGearSetDutyCycleRating
'''


from mastapy.gears.rating import _328
from mastapy._internal.python_net import python_net_import

_CONCEPT_GEAR_SET_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Concept', 'ConceptGearSetDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptGearSetDutyCycleRating',)


class ConceptGearSetDutyCycleRating(_328.GearSetDutyCycleRating):
    '''ConceptGearSetDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_GEAR_SET_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptGearSetDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
