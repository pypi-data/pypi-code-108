'''_1442.py

Impulse
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_IMPULSE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Impulse')


__docformat__ = 'restructuredtext en'
__all__ = ('Impulse',)


class Impulse(_1398.MeasurementBase):
    '''Impulse

    This is a mastapy class.
    '''

    TYPE = _IMPULSE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Impulse.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
