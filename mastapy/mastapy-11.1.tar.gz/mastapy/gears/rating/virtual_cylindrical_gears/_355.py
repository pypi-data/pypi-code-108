'''_355.py

VirtualCylindricalGearBasic
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_VIRTUAL_CYLINDRICAL_GEAR_BASIC = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'VirtualCylindricalGearBasic')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualCylindricalGearBasic',)


class VirtualCylindricalGearBasic(_0.APIBase):
    '''VirtualCylindricalGearBasic

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_CYLINDRICAL_GEAR_BASIC

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualCylindricalGearBasic.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def helix_angle_of_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'HelixAngleOfVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleOfVirtualCylindricalGears

    @property
    def normal_module(self) -> 'float':
        '''float: 'NormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalModule

    @property
    def helix_angle_at_base_circle_of_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'HelixAngleAtBaseCircleOfVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleAtBaseCircleOfVirtualCylindricalGears

    @property
    def tip_diameter_of_virtual_cylindrical_gear(self) -> 'float':
        '''float: 'TipDiameterOfVirtualCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipDiameterOfVirtualCylindricalGear

    @property
    def tip_radius_of_virtual_cylindrical_gear(self) -> 'float':
        '''float: 'TipRadiusOfVirtualCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipRadiusOfVirtualCylindricalGear

    @property
    def reference_diameter_of_virtual_cylindrical_gear(self) -> 'float':
        '''float: 'ReferenceDiameterOfVirtualCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceDiameterOfVirtualCylindricalGear

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
