'''_1199.py

ISO4156SplineHalfDesign
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines import _1219
from mastapy._internal.python_net import python_net_import

_ISO4156_SPLINE_HALF_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'ISO4156SplineHalfDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO4156SplineHalfDesign',)


class ISO4156SplineHalfDesign(_1219.StandardSplineHalfDesign):
    '''ISO4156SplineHalfDesign

    This is a mastapy class.
    '''

    TYPE = _ISO4156_SPLINE_HALF_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO4156SplineHalfDesign.TYPE'):
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
    def minimum_actual_space_width(self) -> 'float':
        '''float: 'MinimumActualSpaceWidth' is the original name of this property.'''

        return self.wrapped.MinimumActualSpaceWidth

    @minimum_actual_space_width.setter
    def minimum_actual_space_width(self, value: 'float'):
        self.wrapped.MinimumActualSpaceWidth = float(value) if value else 0.0

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
    def maximum_effective_tooth_thickness(self) -> 'float':
        '''float: 'MaximumEffectiveToothThickness' is the original name of this property.'''

        return self.wrapped.MaximumEffectiveToothThickness

    @maximum_effective_tooth_thickness.setter
    def maximum_effective_tooth_thickness(self, value: 'float'):
        self.wrapped.MaximumEffectiveToothThickness = float(value) if value else 0.0

    @property
    def maximum_actual_tooth_thickness(self) -> 'float':
        '''float: 'MaximumActualToothThickness' is the original name of this property.'''

        return self.wrapped.MaximumActualToothThickness

    @maximum_actual_tooth_thickness.setter
    def maximum_actual_tooth_thickness(self, value: 'float'):
        self.wrapped.MaximumActualToothThickness = float(value) if value else 0.0

    @property
    def minimum_effective_tooth_thickness(self) -> 'float':
        '''float: 'MinimumEffectiveToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveToothThickness

    @property
    def minimum_actual_tooth_thickness(self) -> 'float':
        '''float: 'MinimumActualToothThickness' is the original name of this property.'''

        return self.wrapped.MinimumActualToothThickness

    @minimum_actual_tooth_thickness.setter
    def minimum_actual_tooth_thickness(self, value: 'float'):
        self.wrapped.MinimumActualToothThickness = float(value) if value else 0.0

    @property
    def maximum_major_diameter(self) -> 'float':
        '''float: 'MaximumMajorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumMajorDiameter

    @property
    def minimum_major_diameter(self) -> 'float':
        '''float: 'MinimumMajorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumMajorDiameter

    @property
    def maximum_minor_diameter(self) -> 'float':
        '''float: 'MaximumMinorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumMinorDiameter

    @property
    def minimum_minor_diameter(self) -> 'float':
        '''float: 'MinimumMinorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumMinorDiameter

    @property
    def minimum_maximum_form_diameter(self) -> 'float':
        '''float: 'MinimumMaximumFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumMaximumFormDiameter

    @property
    def minimum_dimension_over_balls(self) -> 'float':
        '''float: 'MinimumDimensionOverBalls' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumDimensionOverBalls

    @property
    def maximum_dimension_over_balls(self) -> 'float':
        '''float: 'MaximumDimensionOverBalls' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumDimensionOverBalls

    @property
    def basic_rack_addendum_factor(self) -> 'float':
        '''float: 'BasicRackAddendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackAddendumFactor

    @property
    def basic_rack_dedendum_factor(self) -> 'float':
        '''float: 'BasicRackDedendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackDedendumFactor
