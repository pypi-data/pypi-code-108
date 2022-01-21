'''_1193.py

DIN5480SplineJointDesign
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.detailed_rigid_connectors.splines import _1220
from mastapy._internal.python_net import python_net_import

_DIN5480_SPLINE_JOINT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'DIN5480SplineJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('DIN5480SplineJointDesign',)


class DIN5480SplineJointDesign(_1220.StandardSplineJointDesign):
    '''DIN5480SplineJointDesign

    This is a mastapy class.
    '''

    TYPE = _DIN5480_SPLINE_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DIN5480SplineJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def reference_diameter(self) -> 'float':
        '''float: 'ReferenceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceDiameter

    @property
    def addendum_modification_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AddendumModificationFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AddendumModificationFactor) if self.wrapped.AddendumModificationFactor is not None else None

    @addendum_modification_factor.setter
    def addendum_modification_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AddendumModificationFactor = value

    @property
    def base_diameter(self) -> 'float':
        '''float: 'BaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameter

    @property
    def pitch_diameter(self) -> 'float':
        '''float: 'PitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PitchDiameter

    @property
    def minimum_form_clearance(self) -> 'float':
        '''float: 'MinimumFormClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumFormClearance

    @property
    def nominal_space_width(self) -> 'float':
        '''float: 'NominalSpaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalSpaceWidth

    @property
    def nominal_tooth_thickness(self) -> 'float':
        '''float: 'NominalToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalToothThickness
