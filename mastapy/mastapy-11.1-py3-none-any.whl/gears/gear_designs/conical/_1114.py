'''_1114.py

KimosBevelHypoidSingleRotationAngleResult
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_KIMOS_BEVEL_HYPOID_SINGLE_ROTATION_ANGLE_RESULT = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'KimosBevelHypoidSingleRotationAngleResult')


__docformat__ = 'restructuredtext en'
__all__ = ('KimosBevelHypoidSingleRotationAngleResult',)


class KimosBevelHypoidSingleRotationAngleResult(_0.APIBase):
    '''KimosBevelHypoidSingleRotationAngleResult

    This is a mastapy class.
    '''

    TYPE = _KIMOS_BEVEL_HYPOID_SINGLE_ROTATION_ANGLE_RESULT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KimosBevelHypoidSingleRotationAngleResult.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pinion_rotation_angle(self) -> 'float':
        '''float: 'PinionRotationAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionRotationAngle

    @property
    def linear_transmission_error_unloaded(self) -> 'float':
        '''float: 'LinearTransmissionErrorUnloaded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LinearTransmissionErrorUnloaded

    @property
    def linear_transmission_error_loaded(self) -> 'float':
        '''float: 'LinearTransmissionErrorLoaded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LinearTransmissionErrorLoaded

    @property
    def mesh_stiffness_per_unit_face_width(self) -> 'float':
        '''float: 'MeshStiffnessPerUnitFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshStiffnessPerUnitFaceWidth

    @property
    def maximum_pinion_root_stress(self) -> 'float':
        '''float: 'MaximumPinionRootStress' is the original name of this property.'''

        return self.wrapped.MaximumPinionRootStress

    @maximum_pinion_root_stress.setter
    def maximum_pinion_root_stress(self, value: 'float'):
        self.wrapped.MaximumPinionRootStress = float(value) if value else 0.0

    @property
    def maximum_wheel_root_stress(self) -> 'float':
        '''float: 'MaximumWheelRootStress' is the original name of this property.'''

        return self.wrapped.MaximumWheelRootStress

    @maximum_wheel_root_stress.setter
    def maximum_wheel_root_stress(self, value: 'float'):
        self.wrapped.MaximumWheelRootStress = float(value) if value else 0.0
