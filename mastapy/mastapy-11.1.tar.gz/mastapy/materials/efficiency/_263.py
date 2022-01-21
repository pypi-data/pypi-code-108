'''_263.py

IndependentPowerLoss
'''


from mastapy._internal import constructor
from mastapy.materials.efficiency import _270
from mastapy._internal.python_net import python_net_import

_INDEPENDENT_POWER_LOSS = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'IndependentPowerLoss')


__docformat__ = 'restructuredtext en'
__all__ = ('IndependentPowerLoss',)


class IndependentPowerLoss(_270.PowerLoss):
    '''IndependentPowerLoss

    This is a mastapy class.
    '''

    TYPE = _INDEPENDENT_POWER_LOSS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'IndependentPowerLoss.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_dependent_power_loss(self) -> 'float':
        '''float: 'LoadDependentPowerLoss' is the original name of this property.'''

        return self.wrapped.LoadDependentPowerLoss

    @load_dependent_power_loss.setter
    def load_dependent_power_loss(self, value: 'float'):
        self.wrapped.LoadDependentPowerLoss = float(value) if value else 0.0

    @property
    def speed_dependent_power_loss(self) -> 'float':
        '''float: 'SpeedDependentPowerLoss' is the original name of this property.'''

        return self.wrapped.SpeedDependentPowerLoss

    @speed_dependent_power_loss.setter
    def speed_dependent_power_loss(self, value: 'float'):
        self.wrapped.SpeedDependentPowerLoss = float(value) if value else 0.0
