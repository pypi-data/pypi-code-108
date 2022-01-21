'''_270.py

PowerLoss
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_POWER_LOSS = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'PowerLoss')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoss',)


class PowerLoss(_0.APIBase):
    '''PowerLoss

    This is a mastapy class.
    '''

    TYPE = _POWER_LOSS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoss.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def total_power_loss(self) -> 'float':
        '''float: 'TotalPowerLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalPowerLoss

    @property
    def power_loss_calculation_details(self) -> 'str':
        '''str: 'PowerLossCalculationDetails' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PowerLossCalculationDetails
