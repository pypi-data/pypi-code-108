'''_309.py

PocketingPowerLossCoefficientsDatabase
'''


from mastapy.utility.databases import _1596
from mastapy.gears import _308
from mastapy._internal.python_net import python_net_import

_POCKETING_POWER_LOSS_COEFFICIENTS_DATABASE = python_net_import('SMT.MastaAPI.Gears', 'PocketingPowerLossCoefficientsDatabase')


__docformat__ = 'restructuredtext en'
__all__ = ('PocketingPowerLossCoefficientsDatabase',)


class PocketingPowerLossCoefficientsDatabase(_1596.NamedDatabase['_308.PocketingPowerLossCoefficients']):
    '''PocketingPowerLossCoefficientsDatabase

    This is a mastapy class.
    '''

    TYPE = _POCKETING_POWER_LOSS_COEFFICIENTS_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PocketingPowerLossCoefficientsDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
