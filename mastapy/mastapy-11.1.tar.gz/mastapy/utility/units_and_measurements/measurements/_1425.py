'''_1425.py

EnergyPerUnitAreaSmall
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ENERGY_PER_UNIT_AREA_SMALL = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'EnergyPerUnitAreaSmall')


__docformat__ = 'restructuredtext en'
__all__ = ('EnergyPerUnitAreaSmall',)


class EnergyPerUnitAreaSmall(_1398.MeasurementBase):
    '''EnergyPerUnitAreaSmall

    This is a mastapy class.
    '''

    TYPE = _ENERGY_PER_UNIT_AREA_SMALL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EnergyPerUnitAreaSmall.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
