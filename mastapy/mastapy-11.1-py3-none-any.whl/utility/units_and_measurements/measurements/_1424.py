'''_1424.py

EnergyPerUnitArea
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ENERGY_PER_UNIT_AREA = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'EnergyPerUnitArea')


__docformat__ = 'restructuredtext en'
__all__ = ('EnergyPerUnitArea',)


class EnergyPerUnitArea(_1398.MeasurementBase):
    '''EnergyPerUnitArea

    This is a mastapy class.
    '''

    TYPE = _ENERGY_PER_UNIT_AREA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EnergyPerUnitArea.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
