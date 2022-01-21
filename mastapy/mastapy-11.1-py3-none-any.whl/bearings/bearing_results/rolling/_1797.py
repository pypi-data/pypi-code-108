'''_1797.py

LoadedTaperRollerBearingElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1776
from mastapy._internal.python_net import python_net_import

_LOADED_TAPER_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedTaperRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedTaperRollerBearingElement',)


class LoadedTaperRollerBearingElement(_1776.LoadedNonBarrelRollerElement):
    '''LoadedTaperRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_TAPER_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedTaperRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_rib_stress(self) -> 'float':
        '''float: 'MaximumRibStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRibStress

    @property
    def height_of_rib_roller_contact_above_race(self) -> 'float':
        '''float: 'HeightOfRibRollerContactAboveRace' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeightOfRibRollerContactAboveRace
