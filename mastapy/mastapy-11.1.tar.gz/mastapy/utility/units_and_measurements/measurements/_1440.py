'''_1440.py

HeatTransferCoefficientForPlasticGearTooth
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_HEAT_TRANSFER_COEFFICIENT_FOR_PLASTIC_GEAR_TOOTH = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'HeatTransferCoefficientForPlasticGearTooth')


__docformat__ = 'restructuredtext en'
__all__ = ('HeatTransferCoefficientForPlasticGearTooth',)


class HeatTransferCoefficientForPlasticGearTooth(_1398.MeasurementBase):
    '''HeatTransferCoefficientForPlasticGearTooth

    This is a mastapy class.
    '''

    TYPE = _HEAT_TRANSFER_COEFFICIENT_FOR_PLASTIC_GEAR_TOOTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HeatTransferCoefficientForPlasticGearTooth.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
