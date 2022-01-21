'''_505.py

ConicalMeshedGearRating
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.conical import _1099
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONICAL_MESHED_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Conical', 'ConicalMeshedGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshedGearRating',)


class ConicalMeshedGearRating(_0.APIBase):
    '''ConicalMeshedGearRating

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESHED_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshedGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def active_flank(self) -> '_1099.ConicalFlanks':
        '''ConicalFlanks: 'ActiveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ActiveFlank)
        return constructor.new(_1099.ConicalFlanks)(value) if value is not None else None

    @property
    def gleason_axial_factor(self) -> 'float':
        '''float: 'GleasonAxialFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GleasonAxialFactor

    @property
    def gleason_separating_factor(self) -> 'float':
        '''float: 'GleasonSeparatingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GleasonSeparatingFactor

    @property
    def normal_force(self) -> 'float':
        '''float: 'NormalForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalForce

    @property
    def tangential_force(self) -> 'float':
        '''float: 'TangentialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialForce

    @property
    def axial_force(self) -> 'float':
        '''float: 'AxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialForce

    @property
    def axial_force_type(self) -> 'str':
        '''str: 'AxialForceType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AxialForceType

    @property
    def radial_force_type(self) -> 'str':
        '''str: 'RadialForceType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialForceType

    @property
    def radial_force(self) -> 'float':
        '''float: 'RadialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadialForce
