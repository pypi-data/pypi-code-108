'''_1436.py

FuelEfficiencyVehicle
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_FUEL_EFFICIENCY_VEHICLE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'FuelEfficiencyVehicle')


__docformat__ = 'restructuredtext en'
__all__ = ('FuelEfficiencyVehicle',)


class FuelEfficiencyVehicle(_1398.MeasurementBase):
    '''FuelEfficiencyVehicle

    This is a mastapy class.
    '''

    TYPE = _FUEL_EFFICIENCY_VEHICLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FuelEfficiencyVehicle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
