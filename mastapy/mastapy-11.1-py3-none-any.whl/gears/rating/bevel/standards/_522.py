'''_522.py

SpiralBevelMeshSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.rating.conical import _506
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel.Standards', 'SpiralBevelMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelMeshSingleFlankRating',)


class SpiralBevelMeshSingleFlankRating(_506.ConicalMeshSingleFlankRating):
    '''SpiralBevelMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def transmitted_tangential_load_at_large_end(self) -> 'float':
        '''float: 'TransmittedTangentialLoadAtLargeEnd' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransmittedTangentialLoadAtLargeEnd

    @property
    def pitch_line_velocity(self) -> 'float':
        '''float: 'PitchLineVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchLineVelocity

    @property
    def dynamic_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicFactorContact) if self.wrapped.DynamicFactorContact is not None else None

    @property
    def dynamic_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicFactorBending) if self.wrapped.DynamicFactorBending is not None else None

    @property
    def size_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SizeFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SizeFactorBending) if self.wrapped.SizeFactorBending is not None else None

    @property
    def reliability_factor_contact(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReliabilityFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReliabilityFactorContact) if self.wrapped.ReliabilityFactorContact is not None else None

    @property
    def reliability_factor_bending(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ReliabilityFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ReliabilityFactorBending) if self.wrapped.ReliabilityFactorBending is not None else None

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
    def transverse_contact_ratio(self) -> 'float':
        '''float: 'TransverseContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatio

    @property
    def geometry_factor_i(self) -> 'float':
        '''float: 'GeometryFactorI' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorI

    @property
    def pitting_resistance_geometry_factor(self) -> 'float':
        '''float: 'PittingResistanceGeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingResistanceGeometryFactor

    @property
    def inertia_factor_contact(self) -> 'float':
        '''float: 'InertiaFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaFactorContact

    @property
    def length_of_line_of_contact(self) -> 'float':
        '''float: 'LengthOfLineOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfLineOfContact

    @property
    def load_sharing_ratio_contact(self) -> 'float':
        '''float: 'LoadSharingRatioContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioContact

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
    def elastic_coefficient(self) -> 'float':
        '''float: 'ElasticCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElasticCoefficient

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
