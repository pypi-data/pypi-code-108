'''_409.py

GleasonHypoidMeshSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.rating.conical import _506
from mastapy._internal.python_net import python_net_import

_GLEASON_HYPOID_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Hypoid.Standards', 'GleasonHypoidMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GleasonHypoidMeshSingleFlankRating',)


class GleasonHypoidMeshSingleFlankRating(_506.ConicalMeshSingleFlankRating):
    '''GleasonHypoidMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _GLEASON_HYPOID_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GleasonHypoidMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating_standard_name(self) -> 'str':
        '''str: 'RatingStandardName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingStandardName

    @property
    def transmitted_tangential_load_at_large_end(self) -> 'float':
        '''float: 'TransmittedTangentialLoadAtLargeEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransmittedTangentialLoadAtLargeEnd

    @property
    def elastic_coefficient(self) -> 'float':
        '''float: 'ElasticCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticCoefficient

    @property
    def surface_condition_factor(self) -> 'float':
        '''float: 'SurfaceConditionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceConditionFactor

    @property
    def size_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SizeFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SizeFactorBending) if self.wrapped.SizeFactorBending is not None else None

    @property
    def size_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SizeFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SizeFactorContact) if self.wrapped.SizeFactorContact is not None else None

    @property
    def calculated_contact_stress(self) -> 'float':
        '''float: 'CalculatedContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedContactStress

    @property
    def geometry_factor_i(self) -> 'float':
        '''float: 'GeometryFactorI' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorI

    @property
    def load_distribution_factor_contact(self) -> 'float':
        '''float: 'LoadDistributionFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactorContact

    @property
    def load_distribution_factor_bending(self) -> 'float':
        '''float: 'LoadDistributionFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactorBending

    @property
    def temperature_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TemperatureFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TemperatureFactorContact) if self.wrapped.TemperatureFactorContact is not None else None

    @property
    def temperature_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TemperatureFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TemperatureFactorBending) if self.wrapped.TemperatureFactorBending is not None else None

    @property
    def overload_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OverloadFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OverloadFactorContact) if self.wrapped.OverloadFactorContact is not None else None

    @property
    def overload_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OverloadFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OverloadFactorBending) if self.wrapped.OverloadFactorBending is not None else None

    @property
    def dynamic_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicFactorBending) if self.wrapped.DynamicFactorBending is not None else None

    @property
    def dynamic_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicFactorContact) if self.wrapped.DynamicFactorContact is not None else None
