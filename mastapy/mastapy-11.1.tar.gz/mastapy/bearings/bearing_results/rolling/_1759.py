'''_1759.py

LoadedCylindricalRollerBearingRow
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.bearings.bearing_results.rolling import _1758, _1770, _1774
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_LOADED_CYLINDRICAL_ROLLER_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedCylindricalRollerBearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedCylindricalRollerBearingRow',)


class LoadedCylindricalRollerBearingRow(_1774.LoadedNonBarrelRollerBearingRow):
    '''LoadedCylindricalRollerBearingRow

    This is a mastapy class.
    '''

    TYPE = _LOADED_CYLINDRICAL_ROLLER_BEARING_ROW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedCylindricalRollerBearingRow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rib_normal_contact_stress_inner_left(self) -> 'Image':
        '''Image: 'RibNormalContactStressInnerLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.RibNormalContactStressInnerLeft)
        return value

    @property
    def rib_normal_contact_stress_inner_right(self) -> 'Image':
        '''Image: 'RibNormalContactStressInnerRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.RibNormalContactStressInnerRight)
        return value

    @property
    def rib_normal_contact_stress_outer_left(self) -> 'Image':
        '''Image: 'RibNormalContactStressOuterLeft' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.RibNormalContactStressOuterLeft)
        return value

    @property
    def rib_normal_contact_stress_outer_right(self) -> 'Image':
        '''Image: 'RibNormalContactStressOuterRight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.RibNormalContactStressOuterRight)
        return value

    @property
    def loaded_bearing(self) -> '_1758.LoadedCylindricalRollerBearingResults':
        '''LoadedCylindricalRollerBearingResults: 'LoadedBearing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1758.LoadedCylindricalRollerBearingResults.TYPE not in self.wrapped.LoadedBearing.__class__.__mro__:
            raise CastException('Failed to cast loaded_bearing to LoadedCylindricalRollerBearingResults. Expected: {}.'.format(self.wrapped.LoadedBearing.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LoadedBearing.__class__)(self.wrapped.LoadedBearing) if self.wrapped.LoadedBearing is not None else None
