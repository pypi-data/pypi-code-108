'''_779.py

ConicalManufacturingSGTControlParameters
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.bevel.control_parameters import _777
from mastapy._internal.python_net import python_net_import

_CONICAL_MANUFACTURING_SGT_CONTROL_PARAMETERS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel.ControlParameters', 'ConicalManufacturingSGTControlParameters')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalManufacturingSGTControlParameters',)


class ConicalManufacturingSGTControlParameters(_777.ConicalGearManufacturingControlParameters):
    '''ConicalManufacturingSGTControlParameters

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MANUFACTURING_SGT_CONTROL_PARAMETERS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalManufacturingSGTControlParameters.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def root_angle_of_the_pinion(self) -> 'float':
        '''float: 'RootAngleOfThePinion' is the original name of this property.'''

        return self.wrapped.RootAngleOfThePinion

    @root_angle_of_the_pinion.setter
    def root_angle_of_the_pinion(self, value: 'float'):
        self.wrapped.RootAngleOfThePinion = float(value) if value else 0.0

    @property
    def delta_gamma_m(self) -> 'float':
        '''float: 'DeltaGammaM' is the original name of this property.'''

        return self.wrapped.DeltaGammaM

    @delta_gamma_m.setter
    def delta_gamma_m(self, value: 'float'):
        self.wrapped.DeltaGammaM = float(value) if value else 0.0

    @property
    def delta_gamma_x(self) -> 'float':
        '''float: 'DeltaGammaX' is the original name of this property.'''

        return self.wrapped.DeltaGammaX

    @delta_gamma_x.setter
    def delta_gamma_x(self, value: 'float'):
        self.wrapped.DeltaGammaX = float(value) if value else 0.0

    @property
    def delta_ax(self) -> 'float':
        '''float: 'DeltaAX' is the original name of this property.'''

        return self.wrapped.DeltaAX

    @delta_ax.setter
    def delta_ax(self, value: 'float'):
        self.wrapped.DeltaAX = float(value) if value else 0.0
