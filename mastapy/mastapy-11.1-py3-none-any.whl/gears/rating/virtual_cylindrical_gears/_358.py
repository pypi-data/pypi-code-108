'''_358.py

VirtualCylindricalGearSet
'''


from typing import List, Generic, TypeVar

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy.gears.rating.virtual_cylindrical_gears import _355
from mastapy._internal.python_net import python_net_import

_VIRTUAL_CYLINDRICAL_GEAR_SET = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'VirtualCylindricalGearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualCylindricalGearSet',)


T = TypeVar('T', bound='_355.VirtualCylindricalGearBasic')


class VirtualCylindricalGearSet(_0.APIBase, Generic[T]):
    '''VirtualCylindricalGearSet

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _VIRTUAL_CYLINDRICAL_GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualCylindricalGearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def virtual_centre_distance(self) -> 'float':
        '''float: 'VirtualCentreDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualCentreDistance

    @property
    def transverse_contact_ratio_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'TransverseContactRatioForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatioForVirtualCylindricalGears

    @property
    def face_contact_ratio_transverse_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'FaceContactRatioTransverseForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceContactRatioTransverseForVirtualCylindricalGears

    @property
    def virtual_contact_ratio_transverse_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'VirtualContactRatioTransverseForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualContactRatioTransverseForVirtualCylindricalGears

    @property
    def transverse_contact_ratio_normal_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'TransverseContactRatioNormalForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatioNormalForVirtualCylindricalGears

    @property
    def effective_face_width_of_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'EffectiveFaceWidthOfVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidthOfVirtualCylindricalGears

    @property
    def face_width_of_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'FaceWidthOfVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthOfVirtualCylindricalGears

    @property
    def virtual_pinion(self) -> 'T':
        '''T: 'VirtualPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualPinion

    @property
    def virtual_wheel(self) -> 'T':
        '''T: 'VirtualWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualWheel

    @property
    def virtual_cylindrical_gears(self) -> 'List[T]':
        '''List[T]: 'VirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.VirtualCylindricalGears)
        return value
