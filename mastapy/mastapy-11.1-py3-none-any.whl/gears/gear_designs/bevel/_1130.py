'''_1130.py

BevelMeshedGearDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.agma_gleason_conical import _1143
from mastapy._internal.python_net import python_net_import

_BEVEL_MESHED_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'BevelMeshedGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelMeshedGearDesign',)


class BevelMeshedGearDesign(_1143.AGMAGleasonConicalMeshedGearDesign):
    '''BevelMeshedGearDesign

    This is a mastapy class.
    '''

    TYPE = _BEVEL_MESHED_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelMeshedGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def normal_chordal_thickness_at_mean_of_contact(self) -> 'float':
        '''float: 'NormalChordalThicknessAtMeanOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalChordalThicknessAtMeanOfContact

    @property
    def distance_factor(self) -> 'float':
        '''float: 'DistanceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFactor

    @property
    def minimum_root_fillet_radius(self) -> 'float':
        '''float: 'MinimumRootFilletRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumRootFilletRadius

    @property
    def geometry_factor_j_concave(self) -> 'float':
        '''float: 'GeometryFactorJConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorJConcave

    @property
    def geometry_factor_j_convex(self) -> 'float':
        '''float: 'GeometryFactorJConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorJConvex

    @property
    def bending_strength_geometry_factor_concave(self) -> 'float':
        '''float: 'BendingStrengthGeometryFactorConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingStrengthGeometryFactorConcave

    @property
    def bending_strength_geometry_factor_convex(self) -> 'float':
        '''float: 'BendingStrengthGeometryFactorConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingStrengthGeometryFactorConvex

    @property
    def strength_factor_concave(self) -> 'float':
        '''float: 'StrengthFactorConcave' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthFactorConcave

    @property
    def strength_factor_convex(self) -> 'float':
        '''float: 'StrengthFactorConvex' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthFactorConvex

    @property
    def durability_factor_agma(self) -> 'float':
        '''float: 'DurabilityFactorAGMA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DurabilityFactorAGMA

    @property
    def durability_factor_gleason(self) -> 'float':
        '''float: 'DurabilityFactorGleason' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DurabilityFactorGleason
