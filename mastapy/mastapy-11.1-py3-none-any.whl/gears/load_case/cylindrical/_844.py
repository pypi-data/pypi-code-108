'''_844.py

CylindricalMeshLoadCase
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _290, _289
from mastapy.gears.gear_designs.cylindrical import _1014
from mastapy.gears.load_case import _835
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.Gears.LoadCase.Cylindrical', 'CylindricalMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshLoadCase',)


class CylindricalMeshLoadCase(_835.MeshLoadCase):
    '''CylindricalMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def equivalent_misalignment_due_to_system_deflection(self) -> 'float':
        '''float: 'EquivalentMisalignmentDueToSystemDeflection' is the original name of this property.'''

        return self.wrapped.EquivalentMisalignmentDueToSystemDeflection

    @equivalent_misalignment_due_to_system_deflection.setter
    def equivalent_misalignment_due_to_system_deflection(self, value: 'float'):
        self.wrapped.EquivalentMisalignmentDueToSystemDeflection = float(value) if value else 0.0

    @property
    def misalignment_due_to_micro_geometry_lead_relief(self) -> 'float':
        '''float: 'MisalignmentDueToMicroGeometryLeadRelief' is the original name of this property.'''

        return self.wrapped.MisalignmentDueToMicroGeometryLeadRelief

    @misalignment_due_to_micro_geometry_lead_relief.setter
    def misalignment_due_to_micro_geometry_lead_relief(self, value: 'float'):
        self.wrapped.MisalignmentDueToMicroGeometryLeadRelief = float(value) if value else 0.0

    @property
    def equivalent_misalignment(self) -> 'float':
        '''float: 'EquivalentMisalignment' is the original name of this property.'''

        return self.wrapped.EquivalentMisalignment

    @equivalent_misalignment.setter
    def equivalent_misalignment(self, value: 'float'):
        self.wrapped.EquivalentMisalignment = float(value) if value else 0.0

    @property
    def misalignment_source(self) -> '_290.CylindricalMisalignmentDataSource':
        '''CylindricalMisalignmentDataSource: 'MisalignmentSource' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MisalignmentSource)
        return constructor.new(_290.CylindricalMisalignmentDataSource)(value) if value is not None else None

    @misalignment_source.setter
    def misalignment_source(self, value: '_290.CylindricalMisalignmentDataSource'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MisalignmentSource = value

    @property
    def active_flank(self) -> '_289.CylindricalFlanks':
        '''CylindricalFlanks: 'ActiveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ActiveFlank)
        return constructor.new(_289.CylindricalFlanks)(value) if value is not None else None

    @property
    def pitch_line_velocity_at_operating_pitch_diameter(self) -> 'float':
        '''float: 'PitchLineVelocityAtOperatingPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchLineVelocityAtOperatingPitchDiameter

    @property
    def load_case_modifiable_settings(self) -> '_1014.LTCALoadCaseModifiableSettings':
        '''LTCALoadCaseModifiableSettings: 'LoadCaseModifiableSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1014.LTCALoadCaseModifiableSettings)(self.wrapped.LoadCaseModifiableSettings) if self.wrapped.LoadCaseModifiableSettings is not None else None
