'''_1434.py

Frequency
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_FREQUENCY = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Frequency')


__docformat__ = 'restructuredtext en'
__all__ = ('Frequency',)


class Frequency(_1398.MeasurementBase):
    '''Frequency

    This is a mastapy class.
    '''

    TYPE = _FREQUENCY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Frequency.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
