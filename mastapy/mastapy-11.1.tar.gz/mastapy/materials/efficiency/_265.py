'''_265.py

LoadAndSpeedCombinedPowerLoss
'''


from mastapy.materials.efficiency import _270
from mastapy._internal.python_net import python_net_import

_LOAD_AND_SPEED_COMBINED_POWER_LOSS = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'LoadAndSpeedCombinedPowerLoss')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadAndSpeedCombinedPowerLoss',)


class LoadAndSpeedCombinedPowerLoss(_270.PowerLoss):
    '''LoadAndSpeedCombinedPowerLoss

    This is a mastapy class.
    '''

    TYPE = _LOAD_AND_SPEED_COMBINED_POWER_LOSS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadAndSpeedCombinedPowerLoss.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
