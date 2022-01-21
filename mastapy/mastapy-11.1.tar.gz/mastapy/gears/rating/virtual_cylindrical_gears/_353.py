'''_353.py

KlingelnbergVirtualCylindricalGearSet
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import _358, _352
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_VIRTUAL_CYLINDRICAL_GEAR_SET = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'KlingelnbergVirtualCylindricalGearSet')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergVirtualCylindricalGearSet',)


class KlingelnbergVirtualCylindricalGearSet(_358.VirtualCylindricalGearSet['_352.KlingelnbergVirtualCylindricalGear']):
    '''KlingelnbergVirtualCylindricalGearSet

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_VIRTUAL_CYLINDRICAL_GEAR_SET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergVirtualCylindricalGearSet.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def effective_face_width(self) -> 'float':
        '''float: 'EffectiveFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidth

    @property
    def virtual_transmission_ratio(self) -> 'float':
        '''float: 'VirtualTransmissionRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualTransmissionRatio

    @property
    def total_contact_ratio_transverse_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'TotalContactRatioTransverseForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalContactRatioTransverseForVirtualCylindricalGears

    @property
    def length_of_path_of_contact_of_virtual_cylindrical_gear_in_transverse_section(self) -> 'float':
        '''float: 'LengthOfPathOfContactOfVirtualCylindricalGearInTransverseSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfPathOfContactOfVirtualCylindricalGearInTransverseSection
