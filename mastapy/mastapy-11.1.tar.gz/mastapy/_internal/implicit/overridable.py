'''overridable.py

Implementations of 'Overridable' in Python.
As Python does not have an implicit operator, this is the next
best solution for implementing these types properly.
'''


from enum import Enum
from typing import Generic, TypeVar

from mastapy._internal import (
    mixins, constructor, enum_with_selected_value_runtime, conversion
)
from mastapy._internal.python_net import python_net_import
from mastapy.materials import _221
from mastapy.gears import (
    _300, _285, _288, _303
)
from mastapy.bearings.bearing_designs.rolling import _1922, _1905, _1899
from mastapy.bearings import _1655
from mastapy.nodal_analysis.dev_tools_analyses import _175
from mastapy.nodal_analysis.fe_export_utility import _151
from mastapy.system_model.fe import _2143
from mastapy.materials.efficiency import _260, _262
from mastapy.bearings.bearing_results import _1697
from mastapy.system_model.part_model import _2219
from mastapy.bearings.bearing_results.rolling import _1725, _1819
from mastapy.gears.rating.cylindrical.iso6336 import _471
from mastapy.system_model.analyses_and_results.static_loads import _6640

_OVERRIDABLE = python_net_import('SMT.MastaAPI.Utility.Property', 'Overridable')


__docformat__ = 'restructuredtext en'
__all__ = (
    'Overridable_float', 'Overridable_int',
    'Overridable_CylindricalGearRatingMethods', 'Overridable_ISOToleranceStandard',
    'Overridable_CoefficientOfFrictionCalculationMethod', 'Overridable_T',
    'Overridable_WidthSeries', 'Overridable_HeightSeries',
    'Overridable_DiameterSeries', 'Overridable_bool',
    'Overridable_SealLocation', 'Overridable_RigidCouplingType',
    'Overridable_BoundaryConditionType', 'Overridable_NodeSelectionDepthOption',
    'Overridable_BearingEfficiencyRatingMethod', 'Overridable_CylindricalRollerMaxAxialLoadMethod',
    'Overridable_ContactRatioRequirements', 'Overridable_MicroGeometryModel',
    'Overridable_UnbalancedMassInclusionOption', 'Overridable_FrictionModelForGyroscopicMoment',
    'Overridable_RollerAnalysisMethod', 'Overridable_HelicalGearMicroGeometryOption',
    'Overridable_EfficiencyRatingMethod', 'Overridable_MeshStiffnessSource'
)


T = TypeVar('T')


class Overridable_float(float, mixins.OverridableMixin):
    '''Overridable_float

    A specific implementation of 'Overridable' for 'float' types.
    '''

    __hash__ = None
    __qualname__ = 'float'

    def __new__(cls, instance_to_wrap: 'Overridable_float.TYPE'):
        return float.__new__(cls, instance_to_wrap.Value if instance_to_wrap.Value is not None else 0.0)

    def __init__(self, instance_to_wrap: 'Overridable_float.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.Value
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def implicit_type(cls) -> 'float':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return float

    @property
    def value(self) -> 'float':
        '''float: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Value

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Overridden

    @property
    def override_value(self) -> 'float':
        '''float: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.OverrideValue

    @property
    def calculated_value(self) -> 'float':
        '''float: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.CalculatedValue


class Overridable_int(int, mixins.OverridableMixin):
    '''Overridable_int

    A specific implementation of 'Overridable' for 'int' types.
    '''

    __hash__ = None
    __qualname__ = 'int'

    def __new__(cls, instance_to_wrap: 'Overridable_int.TYPE'):
        return int.__new__(cls, instance_to_wrap.Value if instance_to_wrap.Value is not None else 0)

    def __init__(self, instance_to_wrap: 'Overridable_int.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.Value
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def implicit_type(cls) -> 'int':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return int

    @property
    def value(self) -> 'int':
        '''int: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Value

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Overridden

    @property
    def override_value(self) -> 'int':
        '''int: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.OverrideValue

    @property
    def calculated_value(self) -> 'int':
        '''int: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.CalculatedValue


class Overridable_CylindricalGearRatingMethods(mixins.OverridableMixin, Enum):
    '''Overridable_CylindricalGearRatingMethods

    A specific implementation of 'Overridable' for 'CylindricalGearRatingMethods' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalGearRatingMethods'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_221.CylindricalGearRatingMethods':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _221.CylindricalGearRatingMethods

    @classmethod
    def implicit_type(cls) -> '_221.CylindricalGearRatingMethods.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _221.CylindricalGearRatingMethods.type_()

    @property
    def value(self) -> '_221.CylindricalGearRatingMethods':
        '''CylindricalGearRatingMethods: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_221.CylindricalGearRatingMethods':
        '''CylindricalGearRatingMethods: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_221.CylindricalGearRatingMethods':
        '''CylindricalGearRatingMethods: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_ISOToleranceStandard(mixins.OverridableMixin, Enum):
    '''Overridable_ISOToleranceStandard

    A specific implementation of 'Overridable' for 'ISOToleranceStandard' types.
    '''

    __hash__ = None
    __qualname__ = 'ISOToleranceStandard'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_300.ISOToleranceStandard':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _300.ISOToleranceStandard

    @classmethod
    def implicit_type(cls) -> '_300.ISOToleranceStandard.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _300.ISOToleranceStandard.type_()

    @property
    def value(self) -> '_300.ISOToleranceStandard':
        '''ISOToleranceStandard: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_300.ISOToleranceStandard':
        '''ISOToleranceStandard: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_300.ISOToleranceStandard':
        '''ISOToleranceStandard: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_CoefficientOfFrictionCalculationMethod(mixins.OverridableMixin, Enum):
    '''Overridable_CoefficientOfFrictionCalculationMethod

    A specific implementation of 'Overridable' for 'CoefficientOfFrictionCalculationMethod' types.
    '''

    __hash__ = None
    __qualname__ = 'CoefficientOfFrictionCalculationMethod'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_285.CoefficientOfFrictionCalculationMethod':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _285.CoefficientOfFrictionCalculationMethod

    @classmethod
    def implicit_type(cls) -> '_285.CoefficientOfFrictionCalculationMethod.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _285.CoefficientOfFrictionCalculationMethod.type_()

    @property
    def value(self) -> '_285.CoefficientOfFrictionCalculationMethod':
        '''CoefficientOfFrictionCalculationMethod: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_285.CoefficientOfFrictionCalculationMethod':
        '''CoefficientOfFrictionCalculationMethod: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_285.CoefficientOfFrictionCalculationMethod':
        '''CoefficientOfFrictionCalculationMethod: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_T(Generic[T], mixins.OverridableMixin):
    '''Overridable_T

    A specific implementation of 'Overridable' for 'T' types.
    '''

    __hash__ = None
    __qualname__ = 'T'

    def __init__(self, instance_to_wrap: 'Overridable_T.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.Value
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def implicit_type(cls) -> 'T':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return T

    @property
    def value(self) -> 'T':
        '''T: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Value

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Overridden

    @property
    def override_value(self) -> 'T':
        '''T: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.OverrideValue

    @property
    def calculated_value(self) -> 'T':
        '''T: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.CalculatedValue


class Overridable_WidthSeries(mixins.OverridableMixin, Enum):
    '''Overridable_WidthSeries

    A specific implementation of 'Overridable' for 'WidthSeries' types.
    '''

    __hash__ = None
    __qualname__ = 'WidthSeries'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1922.WidthSeries':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1922.WidthSeries

    @classmethod
    def implicit_type(cls) -> '_1922.WidthSeries.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1922.WidthSeries.type_()

    @property
    def value(self) -> '_1922.WidthSeries':
        '''WidthSeries: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1922.WidthSeries':
        '''WidthSeries: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1922.WidthSeries':
        '''WidthSeries: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_HeightSeries(mixins.OverridableMixin, Enum):
    '''Overridable_HeightSeries

    A specific implementation of 'Overridable' for 'HeightSeries' types.
    '''

    __hash__ = None
    __qualname__ = 'HeightSeries'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1905.HeightSeries':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1905.HeightSeries

    @classmethod
    def implicit_type(cls) -> '_1905.HeightSeries.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1905.HeightSeries.type_()

    @property
    def value(self) -> '_1905.HeightSeries':
        '''HeightSeries: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1905.HeightSeries':
        '''HeightSeries: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1905.HeightSeries':
        '''HeightSeries: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_DiameterSeries(mixins.OverridableMixin, Enum):
    '''Overridable_DiameterSeries

    A specific implementation of 'Overridable' for 'DiameterSeries' types.
    '''

    __hash__ = None
    __qualname__ = 'DiameterSeries'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1899.DiameterSeries':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1899.DiameterSeries

    @classmethod
    def implicit_type(cls) -> '_1899.DiameterSeries.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1899.DiameterSeries.type_()

    @property
    def value(self) -> '_1899.DiameterSeries':
        '''DiameterSeries: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1899.DiameterSeries':
        '''DiameterSeries: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1899.DiameterSeries':
        '''DiameterSeries: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_bool(mixins.OverridableMixin):
    '''Overridable_bool

    A specific implementation of 'Overridable' for 'bool' types.
    '''

    __hash__ = None
    __qualname__ = 'bool'

    def __new__(cls, instance_to_wrap: 'Overridable_bool.TYPE'):
        return bool.__new__(cls, instance_to_wrap.Value if instance_to_wrap.Value is not None else False)

    def __init__(self, instance_to_wrap: 'Overridable_bool.TYPE'):
        try:
            self.enclosing = instance_to_wrap
            self.wrapped = instance_to_wrap.Value
        except (TypeError, AttributeError):
            pass

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def implicit_type(cls) -> 'bool':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return bool

    @property
    def value(self) -> 'bool':
        '''bool: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Value

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.Overridden

    @property
    def override_value(self) -> 'bool':
        '''bool: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.OverrideValue

    @property
    def calculated_value(self) -> 'bool':
        '''bool: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.enclosing.CalculatedValue

    def __bool__(self):
        return self.value


class Overridable_SealLocation(mixins.OverridableMixin, Enum):
    '''Overridable_SealLocation

    A specific implementation of 'Overridable' for 'SealLocation' types.
    '''

    __hash__ = None
    __qualname__ = 'SealLocation'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1655.SealLocation':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1655.SealLocation

    @classmethod
    def implicit_type(cls) -> '_1655.SealLocation.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1655.SealLocation.type_()

    @property
    def value(self) -> '_1655.SealLocation':
        '''SealLocation: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1655.SealLocation':
        '''SealLocation: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1655.SealLocation':
        '''SealLocation: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_RigidCouplingType(mixins.OverridableMixin, Enum):
    '''Overridable_RigidCouplingType

    A specific implementation of 'Overridable' for 'RigidCouplingType' types.
    '''

    __hash__ = None
    __qualname__ = 'RigidCouplingType'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_175.RigidCouplingType':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _175.RigidCouplingType

    @classmethod
    def implicit_type(cls) -> '_175.RigidCouplingType.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _175.RigidCouplingType.type_()

    @property
    def value(self) -> '_175.RigidCouplingType':
        '''RigidCouplingType: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_175.RigidCouplingType':
        '''RigidCouplingType: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_175.RigidCouplingType':
        '''RigidCouplingType: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_BoundaryConditionType(mixins.OverridableMixin, Enum):
    '''Overridable_BoundaryConditionType

    A specific implementation of 'Overridable' for 'BoundaryConditionType' types.
    '''

    __hash__ = None
    __qualname__ = 'BoundaryConditionType'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_151.BoundaryConditionType':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _151.BoundaryConditionType

    @classmethod
    def implicit_type(cls) -> '_151.BoundaryConditionType.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _151.BoundaryConditionType.type_()

    @property
    def value(self) -> '_151.BoundaryConditionType':
        '''BoundaryConditionType: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_151.BoundaryConditionType':
        '''BoundaryConditionType: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_151.BoundaryConditionType':
        '''BoundaryConditionType: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_NodeSelectionDepthOption(mixins.OverridableMixin, Enum):
    '''Overridable_NodeSelectionDepthOption

    A specific implementation of 'Overridable' for 'NodeSelectionDepthOption' types.
    '''

    __hash__ = None
    __qualname__ = 'NodeSelectionDepthOption'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_2143.NodeSelectionDepthOption':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _2143.NodeSelectionDepthOption

    @classmethod
    def implicit_type(cls) -> '_2143.NodeSelectionDepthOption.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2143.NodeSelectionDepthOption.type_()

    @property
    def value(self) -> '_2143.NodeSelectionDepthOption':
        '''NodeSelectionDepthOption: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_2143.NodeSelectionDepthOption':
        '''NodeSelectionDepthOption: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_2143.NodeSelectionDepthOption':
        '''NodeSelectionDepthOption: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_BearingEfficiencyRatingMethod(mixins.OverridableMixin, Enum):
    '''Overridable_BearingEfficiencyRatingMethod

    A specific implementation of 'Overridable' for 'BearingEfficiencyRatingMethod' types.
    '''

    __hash__ = None
    __qualname__ = 'BearingEfficiencyRatingMethod'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_260.BearingEfficiencyRatingMethod':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _260.BearingEfficiencyRatingMethod

    @classmethod
    def implicit_type(cls) -> '_260.BearingEfficiencyRatingMethod.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _260.BearingEfficiencyRatingMethod.type_()

    @property
    def value(self) -> '_260.BearingEfficiencyRatingMethod':
        '''BearingEfficiencyRatingMethod: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_260.BearingEfficiencyRatingMethod':
        '''BearingEfficiencyRatingMethod: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_260.BearingEfficiencyRatingMethod':
        '''BearingEfficiencyRatingMethod: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_CylindricalRollerMaxAxialLoadMethod(mixins.OverridableMixin, Enum):
    '''Overridable_CylindricalRollerMaxAxialLoadMethod

    A specific implementation of 'Overridable' for 'CylindricalRollerMaxAxialLoadMethod' types.
    '''

    __hash__ = None
    __qualname__ = 'CylindricalRollerMaxAxialLoadMethod'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1697.CylindricalRollerMaxAxialLoadMethod':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1697.CylindricalRollerMaxAxialLoadMethod

    @classmethod
    def implicit_type(cls) -> '_1697.CylindricalRollerMaxAxialLoadMethod.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1697.CylindricalRollerMaxAxialLoadMethod.type_()

    @property
    def value(self) -> '_1697.CylindricalRollerMaxAxialLoadMethod':
        '''CylindricalRollerMaxAxialLoadMethod: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1697.CylindricalRollerMaxAxialLoadMethod':
        '''CylindricalRollerMaxAxialLoadMethod: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1697.CylindricalRollerMaxAxialLoadMethod':
        '''CylindricalRollerMaxAxialLoadMethod: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_ContactRatioRequirements(mixins.OverridableMixin, Enum):
    '''Overridable_ContactRatioRequirements

    A specific implementation of 'Overridable' for 'ContactRatioRequirements' types.
    '''

    __hash__ = None
    __qualname__ = 'ContactRatioRequirements'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_288.ContactRatioRequirements':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _288.ContactRatioRequirements

    @classmethod
    def implicit_type(cls) -> '_288.ContactRatioRequirements.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _288.ContactRatioRequirements.type_()

    @property
    def value(self) -> '_288.ContactRatioRequirements':
        '''ContactRatioRequirements: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_288.ContactRatioRequirements':
        '''ContactRatioRequirements: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_288.ContactRatioRequirements':
        '''ContactRatioRequirements: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_MicroGeometryModel(mixins.OverridableMixin, Enum):
    '''Overridable_MicroGeometryModel

    A specific implementation of 'Overridable' for 'MicroGeometryModel' types.
    '''

    __hash__ = None
    __qualname__ = 'MicroGeometryModel'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_303.MicroGeometryModel':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _303.MicroGeometryModel

    @classmethod
    def implicit_type(cls) -> '_303.MicroGeometryModel.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _303.MicroGeometryModel.type_()

    @property
    def value(self) -> '_303.MicroGeometryModel':
        '''MicroGeometryModel: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_303.MicroGeometryModel':
        '''MicroGeometryModel: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_303.MicroGeometryModel':
        '''MicroGeometryModel: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_UnbalancedMassInclusionOption(mixins.OverridableMixin, Enum):
    '''Overridable_UnbalancedMassInclusionOption

    A specific implementation of 'Overridable' for 'UnbalancedMassInclusionOption' types.
    '''

    __hash__ = None
    __qualname__ = 'UnbalancedMassInclusionOption'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_2219.UnbalancedMassInclusionOption':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _2219.UnbalancedMassInclusionOption

    @classmethod
    def implicit_type(cls) -> '_2219.UnbalancedMassInclusionOption.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _2219.UnbalancedMassInclusionOption.type_()

    @property
    def value(self) -> '_2219.UnbalancedMassInclusionOption':
        '''UnbalancedMassInclusionOption: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_2219.UnbalancedMassInclusionOption':
        '''UnbalancedMassInclusionOption: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_2219.UnbalancedMassInclusionOption':
        '''UnbalancedMassInclusionOption: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_FrictionModelForGyroscopicMoment(mixins.OverridableMixin, Enum):
    '''Overridable_FrictionModelForGyroscopicMoment

    A specific implementation of 'Overridable' for 'FrictionModelForGyroscopicMoment' types.
    '''

    __hash__ = None
    __qualname__ = 'FrictionModelForGyroscopicMoment'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1725.FrictionModelForGyroscopicMoment':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1725.FrictionModelForGyroscopicMoment

    @classmethod
    def implicit_type(cls) -> '_1725.FrictionModelForGyroscopicMoment.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1725.FrictionModelForGyroscopicMoment.type_()

    @property
    def value(self) -> '_1725.FrictionModelForGyroscopicMoment':
        '''FrictionModelForGyroscopicMoment: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1725.FrictionModelForGyroscopicMoment':
        '''FrictionModelForGyroscopicMoment: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1725.FrictionModelForGyroscopicMoment':
        '''FrictionModelForGyroscopicMoment: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_RollerAnalysisMethod(mixins.OverridableMixin, Enum):
    '''Overridable_RollerAnalysisMethod

    A specific implementation of 'Overridable' for 'RollerAnalysisMethod' types.
    '''

    __hash__ = None
    __qualname__ = 'RollerAnalysisMethod'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_1819.RollerAnalysisMethod':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _1819.RollerAnalysisMethod

    @classmethod
    def implicit_type(cls) -> '_1819.RollerAnalysisMethod.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _1819.RollerAnalysisMethod.type_()

    @property
    def value(self) -> '_1819.RollerAnalysisMethod':
        '''RollerAnalysisMethod: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_1819.RollerAnalysisMethod':
        '''RollerAnalysisMethod: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_1819.RollerAnalysisMethod':
        '''RollerAnalysisMethod: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_HelicalGearMicroGeometryOption(mixins.OverridableMixin, Enum):
    '''Overridable_HelicalGearMicroGeometryOption

    A specific implementation of 'Overridable' for 'HelicalGearMicroGeometryOption' types.
    '''

    __hash__ = None
    __qualname__ = 'HelicalGearMicroGeometryOption'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_471.HelicalGearMicroGeometryOption':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _471.HelicalGearMicroGeometryOption

    @classmethod
    def implicit_type(cls) -> '_471.HelicalGearMicroGeometryOption.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _471.HelicalGearMicroGeometryOption.type_()

    @property
    def value(self) -> '_471.HelicalGearMicroGeometryOption':
        '''HelicalGearMicroGeometryOption: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_471.HelicalGearMicroGeometryOption':
        '''HelicalGearMicroGeometryOption: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_471.HelicalGearMicroGeometryOption':
        '''HelicalGearMicroGeometryOption: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_EfficiencyRatingMethod(mixins.OverridableMixin, Enum):
    '''Overridable_EfficiencyRatingMethod

    A specific implementation of 'Overridable' for 'EfficiencyRatingMethod' types.
    '''

    __hash__ = None
    __qualname__ = 'EfficiencyRatingMethod'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_262.EfficiencyRatingMethod':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _262.EfficiencyRatingMethod

    @classmethod
    def implicit_type(cls) -> '_262.EfficiencyRatingMethod.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _262.EfficiencyRatingMethod.type_()

    @property
    def value(self) -> '_262.EfficiencyRatingMethod':
        '''EfficiencyRatingMethod: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_262.EfficiencyRatingMethod':
        '''EfficiencyRatingMethod: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_262.EfficiencyRatingMethod':
        '''EfficiencyRatingMethod: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None


class Overridable_MeshStiffnessSource(mixins.OverridableMixin, Enum):
    '''Overridable_MeshStiffnessSource

    A specific implementation of 'Overridable' for 'MeshStiffnessSource' types.
    '''

    __hash__ = None
    __qualname__ = 'MeshStiffnessSource'

    @classmethod
    def wrapper_type(cls) -> '_OVERRIDABLE':
        '''Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _OVERRIDABLE

    @classmethod
    def wrapped_type(cls) -> '_6640.MeshStiffnessSource':
        '''Wrapped Pythonnet type of this class.

        Note:
            This property is readonly
        '''

        return _6640.MeshStiffnessSource

    @classmethod
    def implicit_type(cls) -> '_6640.MeshStiffnessSource.type_()':
        '''Implicit Pythonnet type of this class.

        Note:
            This property is readonly.
        '''

        return _6640.MeshStiffnessSource.type_()

    @property
    def value(self) -> '_6640.MeshStiffnessSource':
        '''MeshStiffnessSource: 'Value' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def overridden(self) -> 'bool':
        '''bool: 'Overridden' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def override_value(self) -> '_6640.MeshStiffnessSource':
        '''MeshStiffnessSource: 'OverrideValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None

    @property
    def calculated_value(self) -> '_6640.MeshStiffnessSource':
        '''MeshStiffnessSource: 'CalculatedValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return None
