'''_1757.py

LoadedCylindricalRollerBearingElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1776
from mastapy._internal.python_net import python_net_import

_LOADED_CYLINDRICAL_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedCylindricalRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedCylindricalRollerBearingElement',)


class LoadedCylindricalRollerBearingElement(_1776.LoadedNonBarrelRollerElement):
    '''LoadedCylindricalRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_CYLINDRICAL_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedCylindricalRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_rib_stress_inner_left(self) -> 'float':
        '''float: 'MaximumRibStressInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRibStressInnerLeft

    @property
    def maximum_rib_stress_inner_right(self) -> 'float':
        '''float: 'MaximumRibStressInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRibStressInnerRight

    @property
    def maximum_rib_stress_outer_left(self) -> 'float':
        '''float: 'MaximumRibStressOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRibStressOuterLeft

    @property
    def maximum_rib_stress_outer_right(self) -> 'float':
        '''float: 'MaximumRibStressOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRibStressOuterRight

    @property
    def height_of_rib_roller_contact_above_race_inner_left(self) -> 'float':
        '''float: 'HeightOfRibRollerContactAboveRaceInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeightOfRibRollerContactAboveRaceInnerLeft

    @property
    def height_of_rib_roller_contact_above_race_inner_right(self) -> 'float':
        '''float: 'HeightOfRibRollerContactAboveRaceInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeightOfRibRollerContactAboveRaceInnerRight

    @property
    def height_of_rib_roller_contact_above_race_outer_left(self) -> 'float':
        '''float: 'HeightOfRibRollerContactAboveRaceOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeightOfRibRollerContactAboveRaceOuterLeft

    @property
    def height_of_rib_roller_contact_above_race_outer_right(self) -> 'float':
        '''float: 'HeightOfRibRollerContactAboveRaceOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HeightOfRibRollerContactAboveRaceOuterRight
