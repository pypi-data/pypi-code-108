'''_1405.py

Acceleration
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ACCELERATION = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Acceleration')


__docformat__ = 'restructuredtext en'
__all__ = ('Acceleration',)


class Acceleration(_1398.MeasurementBase):
    '''Acceleration

    This is a mastapy class.
    '''

    TYPE = _ACCELERATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Acceleration.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
