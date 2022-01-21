'''_1469.py

Percentage
'''


from mastapy.utility.units_and_measurements.measurements import _1433
from mastapy._internal.python_net import python_net_import

_PERCENTAGE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Percentage')


__docformat__ = 'restructuredtext en'
__all__ = ('Percentage',)


class Percentage(_1433.FractionMeasurementBase):
    '''Percentage

    This is a mastapy class.
    '''

    TYPE = _PERCENTAGE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Percentage.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
