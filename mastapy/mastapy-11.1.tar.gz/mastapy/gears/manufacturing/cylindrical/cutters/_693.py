'''_693.py

CylindricalGearShaver
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.manufacturing.cylindrical.cutters import _696
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SHAVER = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'CylindricalGearShaver')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearShaver',)


class CylindricalGearShaver(_696.InvoluteCutterDesign):
    '''CylindricalGearShaver

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SHAVER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearShaver.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def base_diameter(self) -> 'float':
        '''float: 'BaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameter

    @property
    def has_tolerances(self) -> 'bool':
        '''bool: 'HasTolerances' is the original name of this property.'''

        return self.wrapped.HasTolerances

    @has_tolerances.setter
    def has_tolerances(self, value: 'bool'):
        self.wrapped.HasTolerances = bool(value) if value else False

    @property
    def tip_diameter(self) -> 'float':
        '''float: 'TipDiameter' is the original name of this property.'''

        return self.wrapped.TipDiameter

    @tip_diameter.setter
    def tip_diameter(self, value: 'float'):
        self.wrapped.TipDiameter = float(value) if value else 0.0

    @property
    def root_form_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RootFormDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RootFormDiameter) if self.wrapped.RootFormDiameter is not None else None

    @root_form_diameter.setter
    def root_form_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RootFormDiameter = value

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def normal_tip_thickness(self) -> 'float':
        '''float: 'NormalTipThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalTipThickness
