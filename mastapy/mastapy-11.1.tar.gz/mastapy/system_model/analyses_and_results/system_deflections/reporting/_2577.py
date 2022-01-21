'''_2577.py

CylindricalGearMeshMisalignmentValue
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MESH_MISALIGNMENT_VALUE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting', 'CylindricalGearMeshMisalignmentValue')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMeshMisalignmentValue',)


class CylindricalGearMeshMisalignmentValue(_0.APIBase):
    '''CylindricalGearMeshMisalignmentValue

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MESH_MISALIGNMENT_VALUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMeshMisalignmentValue.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_name(self) -> 'str':
        '''str: 'GearName' is the original name of this property.'''

        return self.wrapped.GearName

    @gear_name.setter
    def gear_name(self, value: 'str'):
        self.wrapped.GearName = str(value) if value else ''

    @property
    def misalignment(self) -> 'float':
        '''float: 'Misalignment' is the original name of this property.'''

        return self.wrapped.Misalignment

    @misalignment.setter
    def misalignment(self, value: 'float'):
        self.wrapped.Misalignment = float(value) if value else 0.0

    @property
    def misalignment_due_to_twist(self) -> 'float':
        '''float: 'MisalignmentDueToTwist' is the original name of this property.'''

        return self.wrapped.MisalignmentDueToTwist

    @misalignment_due_to_twist.setter
    def misalignment_due_to_twist(self, value: 'float'):
        self.wrapped.MisalignmentDueToTwist = float(value) if value else 0.0

    @property
    def misalignment_due_to_tilt(self) -> 'float':
        '''float: 'MisalignmentDueToTilt' is the original name of this property.'''

        return self.wrapped.MisalignmentDueToTilt

    @misalignment_due_to_tilt.setter
    def misalignment_due_to_tilt(self, value: 'float'):
        self.wrapped.MisalignmentDueToTilt = float(value) if value else 0.0

    @property
    def tilt_x(self) -> 'float':
        '''float: 'TiltX' is the original name of this property.'''

        return self.wrapped.TiltX

    @tilt_x.setter
    def tilt_x(self, value: 'float'):
        self.wrapped.TiltX = float(value) if value else 0.0

    @property
    def tilt_y(self) -> 'float':
        '''float: 'TiltY' is the original name of this property.'''

        return self.wrapped.TiltY

    @tilt_y.setter
    def tilt_y(self, value: 'float'):
        self.wrapped.TiltY = float(value) if value else 0.0
