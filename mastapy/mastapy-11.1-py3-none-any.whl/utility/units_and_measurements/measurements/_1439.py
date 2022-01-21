'''_1439.py

HeatTransfer
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_HEAT_TRANSFER = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'HeatTransfer')


__docformat__ = 'restructuredtext en'
__all__ = ('HeatTransfer',)


class HeatTransfer(_1398.MeasurementBase):
    '''HeatTransfer

    This is a mastapy class.
    '''

    TYPE = _HEAT_TRANSFER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HeatTransfer.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
