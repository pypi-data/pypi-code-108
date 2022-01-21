'''_2113.py

DegreeOfFreedomBoundaryConditionAngular
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.fe import _2112
from mastapy._internal.python_net import python_net_import

_DEGREE_OF_FREEDOM_BOUNDARY_CONDITION_ANGULAR = python_net_import('SMT.MastaAPI.SystemModel.FE', 'DegreeOfFreedomBoundaryConditionAngular')


__docformat__ = 'restructuredtext en'
__all__ = ('DegreeOfFreedomBoundaryConditionAngular',)


class DegreeOfFreedomBoundaryConditionAngular(_2112.DegreeOfFreedomBoundaryCondition):
    '''DegreeOfFreedomBoundaryConditionAngular

    This is a mastapy class.
    '''

    TYPE = _DEGREE_OF_FREEDOM_BOUNDARY_CONDITION_ANGULAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DegreeOfFreedomBoundaryConditionAngular.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'Angle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.Angle) if self.wrapped.Angle is not None else None

    @angle.setter
    def angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.Angle = value

    @property
    def torque(self) -> 'float':
        '''float: 'Torque' is the original name of this property.'''

        return self.wrapped.Torque

    @torque.setter
    def torque(self, value: 'float'):
        self.wrapped.Torque = float(value) if value else 0.0
