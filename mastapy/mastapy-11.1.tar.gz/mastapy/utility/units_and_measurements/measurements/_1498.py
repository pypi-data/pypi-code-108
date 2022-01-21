'''_1498.py

ThermoElasticFactor
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_THERMO_ELASTIC_FACTOR = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'ThermoElasticFactor')


__docformat__ = 'restructuredtext en'
__all__ = ('ThermoElasticFactor',)


class ThermoElasticFactor(_1398.MeasurementBase):
    '''ThermoElasticFactor

    This is a mastapy class.
    '''

    TYPE = _THERMO_ELASTIC_FACTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ThermoElasticFactor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
