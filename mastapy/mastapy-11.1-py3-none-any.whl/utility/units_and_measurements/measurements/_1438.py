'''_1438.py

HeatConductivity
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_HEAT_CONDUCTIVITY = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'HeatConductivity')


__docformat__ = 'restructuredtext en'
__all__ = ('HeatConductivity',)


class HeatConductivity(_1398.MeasurementBase):
    '''HeatConductivity

    This is a mastapy class.
    '''

    TYPE = _HEAT_CONDUCTIVITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HeatConductivity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
