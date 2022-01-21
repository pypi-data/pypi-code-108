'''_1207.py

SAESplineHalfDesign
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines.tolerances_and_deviations import _1222
from mastapy.detailed_rigid_connectors.splines import _1219
from mastapy._internal.python_net import python_net_import

_SAE_SPLINE_HALF_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'SAESplineHalfDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('SAESplineHalfDesign',)


class SAESplineHalfDesign(_1219.StandardSplineHalfDesign):
    '''SAESplineHalfDesign

    This is a mastapy class.
    '''

    TYPE = _SAE_SPLINE_HALF_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SAESplineHalfDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def minimum_effective_space_width(self) -> 'float':
        '''float: 'MinimumEffectiveSpaceWidth' is the original name of this property.'''

        return self.wrapped.MinimumEffectiveSpaceWidth

    @minimum_effective_space_width.setter
    def minimum_effective_space_width(self, value: 'float'):
        self.wrapped.MinimumEffectiveSpaceWidth = float(value) if value else 0.0

    @property
    def maximum_actual_space_width(self) -> 'float':
        '''float: 'MaximumActualSpaceWidth' is the original name of this property.'''

        return self.wrapped.MaximumActualSpaceWidth

    @maximum_actual_space_width.setter
    def maximum_actual_space_width(self, value: 'float'):
        self.wrapped.MaximumActualSpaceWidth = float(value) if value else 0.0

    @property
    def maximum_effective_space_width(self) -> 'float':
        '''float: 'MaximumEffectiveSpaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEffectiveSpaceWidth

    @property
    def minimum_effective_tooth_thickness(self) -> 'float':
        '''float: 'MinimumEffectiveToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveToothThickness

    @property
    def minimum_actual_space_width(self) -> 'float':
        '''float: 'MinimumActualSpaceWidth' is the original name of this property.'''

        return self.wrapped.MinimumActualSpaceWidth

    @minimum_actual_space_width.setter
    def minimum_actual_space_width(self, value: 'float'):
        self.wrapped.MinimumActualSpaceWidth = float(value) if value else 0.0

    @property
    def maximum_effective_tooth_thickness(self) -> 'float':
        '''float: 'MaximumEffectiveToothThickness' is the original name of this property.'''

        return self.wrapped.MaximumEffectiveToothThickness

    @maximum_effective_tooth_thickness.setter
    def maximum_effective_tooth_thickness(self, value: 'float'):
        self.wrapped.MaximumEffectiveToothThickness = float(value) if value else 0.0

    @property
    def minimum_actual_tooth_thickness(self) -> 'float':
        '''float: 'MinimumActualToothThickness' is the original name of this property.'''

        return self.wrapped.MinimumActualToothThickness

    @minimum_actual_tooth_thickness.setter
    def minimum_actual_tooth_thickness(self, value: 'float'):
        self.wrapped.MinimumActualToothThickness = float(value) if value else 0.0

    @property
    def maximum_actual_tooth_thickness(self) -> 'float':
        '''float: 'MaximumActualToothThickness' is the original name of this property.'''

        return self.wrapped.MaximumActualToothThickness

    @maximum_actual_tooth_thickness.setter
    def maximum_actual_tooth_thickness(self, value: 'float'):
        self.wrapped.MaximumActualToothThickness = float(value) if value else 0.0

    @property
    def minimum_major_diameter(self) -> 'float':
        '''float: 'MinimumMajorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumMajorDiameter

    @property
    def maximum_major_diameter(self) -> 'float':
        '''float: 'MaximumMajorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumMajorDiameter

    @property
    def form_diameter(self) -> 'float':
        '''float: 'FormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormDiameter

    @property
    def change_in_root_diameter(self) -> 'float':
        '''float: 'ChangeInRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChangeInRootDiameter

    @property
    def maximum_dimension_over_balls(self) -> 'float':
        '''float: 'MaximumDimensionOverBalls' is the original name of this property.'''

        return self.wrapped.MaximumDimensionOverBalls

    @maximum_dimension_over_balls.setter
    def maximum_dimension_over_balls(self, value: 'float'):
        self.wrapped.MaximumDimensionOverBalls = float(value) if value else 0.0

    @property
    def minimum_dimension_over_balls(self) -> 'float':
        '''float: 'MinimumDimensionOverBalls' is the original name of this property.'''

        return self.wrapped.MinimumDimensionOverBalls

    @minimum_dimension_over_balls.setter
    def minimum_dimension_over_balls(self, value: 'float'):
        self.wrapped.MinimumDimensionOverBalls = float(value) if value else 0.0

    @property
    def root_fillet_radius_factor(self) -> 'float':
        '''float: 'RootFilletRadiusFactor' is the original name of this property.'''

        return self.wrapped.RootFilletRadiusFactor

    @root_fillet_radius_factor.setter
    def root_fillet_radius_factor(self, value: 'float'):
        self.wrapped.RootFilletRadiusFactor = float(value) if value else 0.0

    @property
    def sae_accuracy_and_tolerance(self) -> '_1222.SAESplineTolerances':
        '''SAESplineTolerances: 'SAEAccuracyAndTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1222.SAESplineTolerances)(self.wrapped.SAEAccuracyAndTolerance) if self.wrapped.SAEAccuracyAndTolerance is not None else None
