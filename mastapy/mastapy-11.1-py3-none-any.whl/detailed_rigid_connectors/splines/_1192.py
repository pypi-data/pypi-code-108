'''_1192.py

DIN5480SplineHalfDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.detailed_rigid_connectors.splines import _1202, _1211, _1219
from mastapy._internal.python_net import python_net_import

_DIN5480_SPLINE_HALF_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'DIN5480SplineHalfDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('DIN5480SplineHalfDesign',)


class DIN5480SplineHalfDesign(_1219.StandardSplineHalfDesign):
    '''DIN5480SplineHalfDesign

    This is a mastapy class.
    '''

    TYPE = _DIN5480_SPLINE_HALF_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DIN5480SplineHalfDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_actual_space_width(self) -> 'float':
        '''float: 'MaximumActualSpaceWidth' is the original name of this property.'''

        return self.wrapped.MaximumActualSpaceWidth

    @maximum_actual_space_width.setter
    def maximum_actual_space_width(self, value: 'float'):
        self.wrapped.MaximumActualSpaceWidth = float(value) if value else 0.0

    @property
    def minimum_actual_space_width(self) -> 'float':
        '''float: 'MinimumActualSpaceWidth' is the original name of this property.'''

        return self.wrapped.MinimumActualSpaceWidth

    @minimum_actual_space_width.setter
    def minimum_actual_space_width(self, value: 'float'):
        self.wrapped.MinimumActualSpaceWidth = float(value) if value else 0.0

    @property
    def minimum_effective_space_width(self) -> 'float':
        '''float: 'MinimumEffectiveSpaceWidth' is the original name of this property.'''

        return self.wrapped.MinimumEffectiveSpaceWidth

    @minimum_effective_space_width.setter
    def minimum_effective_space_width(self, value: 'float'):
        self.wrapped.MinimumEffectiveSpaceWidth = float(value) if value else 0.0

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
    def minimum_actual_tooth_thickness(self) -> 'float':
        '''float: 'MinimumActualToothThickness' is the original name of this property.'''

        return self.wrapped.MinimumActualToothThickness

    @minimum_actual_tooth_thickness.setter
    def minimum_actual_tooth_thickness(self, value: 'float'):
        self.wrapped.MinimumActualToothThickness = float(value) if value else 0.0

    @property
    def addendum_modification(self) -> 'float':
        '''float: 'AddendumModification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumModification

    @property
    def tip_diameter(self) -> 'float':
        '''float: 'TipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipDiameter

    @property
    def root_diameter(self) -> 'float':
        '''float: 'RootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootDiameter

    @property
    def maximum_effective_root_diameter(self) -> 'float':
        '''float: 'MaximumEffectiveRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEffectiveRootDiameter

    @property
    def minimum_effective_root_diameter(self) -> 'float':
        '''float: 'MinimumEffectiveRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveRootDiameter

    @property
    def base_form_circle_diameter_limit(self) -> 'float':
        '''float: 'BaseFormCircleDiameterLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseFormCircleDiameterLimit

    @property
    def root_fillet_radius_factor(self) -> 'float':
        '''float: 'RootFilletRadiusFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFilletRadiusFactor

    @property
    def manufacturing_type(self) -> '_1202.ManufacturingTypes':
        '''ManufacturingTypes: 'ManufacturingType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ManufacturingType)
        return constructor.new(_1202.ManufacturingTypes)(value) if value is not None else None

    @manufacturing_type.setter
    def manufacturing_type(self, value: '_1202.ManufacturingTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ManufacturingType = value

    @property
    def finishing_method(self) -> '_1211.FinishingMethods':
        '''FinishingMethods: 'FinishingMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FinishingMethod)
        return constructor.new(_1211.FinishingMethods)(value) if value is not None else None

    @finishing_method.setter
    def finishing_method(self, value: '_1211.FinishingMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FinishingMethod = value

    @property
    def tooth_height_of_basic_rack(self) -> 'float':
        '''float: 'ToothHeightOfBasicRack' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothHeightOfBasicRack

    @property
    def bottom_clearance_of_basic_rack(self) -> 'float':
        '''float: 'BottomClearanceOfBasicRack' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BottomClearanceOfBasicRack

    @property
    def addendum_of_basic_rack(self) -> 'float':
        '''float: 'AddendumOfBasicRack' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumOfBasicRack

    @property
    def basic_rack_addendum_factor(self) -> 'float':
        '''float: 'BasicRackAddendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackAddendumFactor

    @property
    def dedendum_of_basic_rack(self) -> 'float':
        '''float: 'DedendumOfBasicRack' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DedendumOfBasicRack

    @property
    def basic_rack_dedendum_factor(self) -> 'float':
        '''float: 'BasicRackDedendumFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicRackDedendumFactor

    @property
    def form_clearance_of_basic_rack(self) -> 'float':
        '''float: 'FormClearanceOfBasicRack' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormClearanceOfBasicRack
