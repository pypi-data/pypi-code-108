'''_1946.py

ConceptRadialClearanceBearing
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import
from mastapy.bearings.bearing_designs.concept import _1945

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CONCEPT_RADIAL_CLEARANCE_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Concept', 'ConceptRadialClearanceBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptRadialClearanceBearing',)


class ConceptRadialClearanceBearing(_1945.ConceptClearanceBearing):
    '''ConceptRadialClearanceBearing

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_RADIAL_CLEARANCE_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptRadialClearanceBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_angle(self) -> 'float':
        '''float: 'ContactAngle' is the original name of this property.'''

        return self.wrapped.ContactAngle

    @contact_angle.setter
    def contact_angle(self, value: 'float'):
        self.wrapped.ContactAngle = float(value) if value else 0.0

    @property
    def contact_diameter_derived_from_connection_geometry(self) -> 'bool':
        '''bool: 'ContactDiameterDerivedFromConnectionGeometry' is the original name of this property.'''

        return self.wrapped.ContactDiameterDerivedFromConnectionGeometry

    @contact_diameter_derived_from_connection_geometry.setter
    def contact_diameter_derived_from_connection_geometry(self, value: 'bool'):
        self.wrapped.ContactDiameterDerivedFromConnectionGeometry = bool(value) if value else False

    @property
    def has_stiffness_only_in_eccentricity_direction(self) -> 'bool':
        '''bool: 'HasStiffnessOnlyInEccentricityDirection' is the original name of this property.'''

        return self.wrapped.HasStiffnessOnlyInEccentricityDirection

    @has_stiffness_only_in_eccentricity_direction.setter
    def has_stiffness_only_in_eccentricity_direction(self, value: 'bool'):
        self.wrapped.HasStiffnessOnlyInEccentricityDirection = bool(value) if value else False

    @property
    def outer_diameter(self) -> 'float':
        '''float: 'OuterDiameter' is the original name of this property.'''

        return self.wrapped.OuterDiameter

    @outer_diameter.setter
    def outer_diameter(self, value: 'float'):
        self.wrapped.OuterDiameter = float(value) if value else 0.0

    @property
    def bore(self) -> 'float':
        '''float: 'Bore' is the original name of this property.'''

        return self.wrapped.Bore

    @bore.setter
    def bore(self, value: 'float'):
        self.wrapped.Bore = float(value) if value else 0.0

    @property
    def start_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'StartAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.StartAngle) if self.wrapped.StartAngle is not None else None

    @start_angle.setter
    def start_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.StartAngle = value

    @property
    def end_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'EndAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.EndAngle) if self.wrapped.EndAngle is not None else None

    @end_angle.setter
    def end_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.EndAngle = value

    @property
    def inner_component_material_selector(self) -> 'str':
        '''str: 'InnerComponentMaterialSelector' is the original name of this property.'''

        return self.wrapped.InnerComponentMaterialSelector.SelectedItemName

    @inner_component_material_selector.setter
    def inner_component_material_selector(self, value: 'str'):
        self.wrapped.InnerComponentMaterialSelector.SetSelectedItem(str(value) if value else '')

    @property
    def outer_component_material_selector(self) -> 'str':
        '''str: 'OuterComponentMaterialSelector' is the original name of this property.'''

        return self.wrapped.OuterComponentMaterialSelector.SelectedItemName

    @outer_component_material_selector.setter
    def outer_component_material_selector(self, value: 'str'):
        self.wrapped.OuterComponentMaterialSelector.SetSelectedItem(str(value) if value else '')
