'''_650.py

RackMountingError
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _639
from mastapy._internal.python_net import python_net_import

_RACK_MOUNTING_ERROR = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'RackMountingError')


__docformat__ = 'restructuredtext en'
__all__ = ('RackMountingError',)


class RackMountingError(_639.MountingError):
    '''RackMountingError

    This is a mastapy class.
    '''

    TYPE = _RACK_MOUNTING_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RackMountingError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def axial_runout(self) -> 'float':
        '''float: 'AxialRunout' is the original name of this property.'''

        return self.wrapped.AxialRunout

    @axial_runout.setter
    def axial_runout(self, value: 'float'):
        self.wrapped.AxialRunout = float(value) if value else 0.0

    @property
    def axial_runout_phase_angle(self) -> 'float':
        '''float: 'AxialRunoutPhaseAngle' is the original name of this property.'''

        return self.wrapped.AxialRunoutPhaseAngle

    @axial_runout_phase_angle.setter
    def axial_runout_phase_angle(self, value: 'float'):
        self.wrapped.AxialRunoutPhaseAngle = float(value) if value else 0.0
