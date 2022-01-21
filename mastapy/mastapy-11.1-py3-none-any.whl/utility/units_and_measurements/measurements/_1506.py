'''_1506.py

Velocity
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_VELOCITY = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Velocity')


__docformat__ = 'restructuredtext en'
__all__ = ('Velocity',)


class Velocity(_1398.MeasurementBase):
    '''Velocity

    This is a mastapy class.
    '''

    TYPE = _VELOCITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Velocity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
