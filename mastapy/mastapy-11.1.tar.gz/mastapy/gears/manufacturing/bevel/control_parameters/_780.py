'''_780.py

ConicalManufacturingSMTControlParameters
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.bevel.control_parameters import _777
from mastapy._internal.python_net import python_net_import

_CONICAL_MANUFACTURING_SMT_CONTROL_PARAMETERS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel.ControlParameters', 'ConicalManufacturingSMTControlParameters')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalManufacturingSMTControlParameters',)


class ConicalManufacturingSMTControlParameters(_777.ConicalGearManufacturingControlParameters):
    '''ConicalManufacturingSMTControlParameters

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MANUFACTURING_SMT_CONTROL_PARAMETERS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalManufacturingSMTControlParameters.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mean_contact_point_h(self) -> 'float':
        '''float: 'MeanContactPointH' is the original name of this property.'''

        return self.wrapped.MeanContactPointH

    @mean_contact_point_h.setter
    def mean_contact_point_h(self, value: 'float'):
        self.wrapped.MeanContactPointH = float(value) if value else 0.0

    @property
    def mean_contact_point_v(self) -> 'float':
        '''float: 'MeanContactPointV' is the original name of this property.'''

        return self.wrapped.MeanContactPointV

    @mean_contact_point_v.setter
    def mean_contact_point_v(self, value: 'float'):
        self.wrapped.MeanContactPointV = float(value) if value else 0.0

    @property
    def initial_workhead_offset(self) -> 'float':
        '''float: 'InitialWorkheadOffset' is the original name of this property.'''

        return self.wrapped.InitialWorkheadOffset

    @initial_workhead_offset.setter
    def initial_workhead_offset(self, value: 'float'):
        self.wrapped.InitialWorkheadOffset = float(value) if value else 0.0

    @property
    def delta_sigma(self) -> 'float':
        '''float: 'DeltaSigma' is the original name of this property.'''

        return self.wrapped.DeltaSigma

    @delta_sigma.setter
    def delta_sigma(self, value: 'float'):
        self.wrapped.DeltaSigma = float(value) if value else 0.0

    @property
    def delta_e(self) -> 'float':
        '''float: 'DeltaE' is the original name of this property.'''

        return self.wrapped.DeltaE

    @delta_e.setter
    def delta_e(self, value: 'float'):
        self.wrapped.DeltaE = float(value) if value else 0.0

    @property
    def delta_xp(self) -> 'float':
        '''float: 'DeltaXP' is the original name of this property.'''

        return self.wrapped.DeltaXP

    @delta_xp.setter
    def delta_xp(self, value: 'float'):
        self.wrapped.DeltaXP = float(value) if value else 0.0

    @property
    def delta_xw(self) -> 'float':
        '''float: 'DeltaXW' is the original name of this property.'''

        return self.wrapped.DeltaXW

    @delta_xw.setter
    def delta_xw(self, value: 'float'):
        self.wrapped.DeltaXW = float(value) if value else 0.0

    @property
    def clearance_between_finish_root_and_rough_root(self) -> 'float':
        '''float: 'ClearanceBetweenFinishRootAndRoughRoot' is the original name of this property.'''

        return self.wrapped.ClearanceBetweenFinishRootAndRoughRoot

    @clearance_between_finish_root_and_rough_root.setter
    def clearance_between_finish_root_and_rough_root(self, value: 'float'):
        self.wrapped.ClearanceBetweenFinishRootAndRoughRoot = float(value) if value else 0.0

    @property
    def angular_acceleration(self) -> 'float':
        '''float: 'AngularAcceleration' is the original name of this property.'''

        return self.wrapped.AngularAcceleration

    @angular_acceleration.setter
    def angular_acceleration(self, value: 'float'):
        self.wrapped.AngularAcceleration = float(value) if value else 0.0

    @property
    def direction_angle_of_poc(self) -> 'float':
        '''float: 'DirectionAngleOfPOC' is the original name of this property.'''

        return self.wrapped.DirectionAngleOfPOC

    @direction_angle_of_poc.setter
    def direction_angle_of_poc(self, value: 'float'):
        self.wrapped.DirectionAngleOfPOC = float(value) if value else 0.0
