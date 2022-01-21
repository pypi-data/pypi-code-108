'''_525.py

AGMAGleasonConicalGearMeshRating
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.conical import _1116
from mastapy.gears.rating.conical import _499
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_MESH_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.AGMAGleasonConical', 'AGMAGleasonConicalGearMeshRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearMeshRating',)


class AGMAGleasonConicalGearMeshRating(_499.ConicalGearMeshRating):
    '''AGMAGleasonConicalGearMeshRating

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_MESH_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearMeshRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def overload_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OverloadFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OverloadFactorBending) if self.wrapped.OverloadFactorBending is not None else None

    @property
    def overload_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OverloadFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OverloadFactorContact) if self.wrapped.OverloadFactorContact is not None else None

    @property
    def maximum_relative_displacement(self) -> 'float':
        '''float: 'MaximumRelativeDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRelativeDisplacement

    @property
    def load_distribution_factor_method(self) -> '_1116.LoadDistributionFactorMethods':
        '''LoadDistributionFactorMethods: 'LoadDistributionFactorMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.LoadDistributionFactorMethod)
        return constructor.new(_1116.LoadDistributionFactorMethods)(value) if value is not None else None
