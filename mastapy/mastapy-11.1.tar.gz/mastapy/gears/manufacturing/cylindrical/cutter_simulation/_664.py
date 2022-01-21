'''_664.py

CylindricalCutterSimulatableGear
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.geometry.two_d import _278
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_CUTTER_SIMULATABLE_GEAR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.CutterSimulation', 'CylindricalCutterSimulatableGear')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalCutterSimulatableGear',)


class CylindricalCutterSimulatableGear(_0.APIBase):
    '''CylindricalCutterSimulatableGear

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_CUTTER_SIMULATABLE_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalCutterSimulatableGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def root_form_diameter(self) -> 'float':
        '''float: 'RootFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFormDiameter

    @property
    def tip_form_diameter(self) -> 'float':
        '''float: 'TipFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipFormDiameter

    @property
    def generating_addendum_modification_factor(self) -> 'float':
        '''float: 'GeneratingAddendumModificationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeneratingAddendumModificationFactor

    @property
    def internal_external(self) -> '_278.InternalExternalType':
        '''InternalExternalType: 'InternalExternal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.InternalExternal)
        return constructor.new(_278.InternalExternalType)(value) if value is not None else None

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def normal_module(self) -> 'float':
        '''float: 'NormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalModule

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngle

    @property
    def normal_thickness(self) -> 'float':
        '''float: 'NormalThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThickness

    @property
    def number_of_teeth_unsigned(self) -> 'float':
        '''float: 'NumberOfTeethUnsigned' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfTeethUnsigned

    @property
    def tip_diameter(self) -> 'float':
        '''float: 'TipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipDiameter

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidth

    @property
    def is_left_handed(self) -> 'bool':
        '''bool: 'IsLeftHanded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLeftHanded

    @property
    def root_diameter(self) -> 'float':
        '''float: 'RootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootDiameter

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngle

    @property
    def reference_diameter(self) -> 'float':
        '''float: 'ReferenceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceDiameter
