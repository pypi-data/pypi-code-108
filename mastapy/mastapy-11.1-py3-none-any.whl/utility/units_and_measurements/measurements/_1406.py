'''_1406.py

Angle
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGLE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Angle')


__docformat__ = 'restructuredtext en'
__all__ = ('Angle',)


class Angle(_1398.MeasurementBase):
    '''Angle

    This is a mastapy class.
    '''

    TYPE = _ANGLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Angle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
