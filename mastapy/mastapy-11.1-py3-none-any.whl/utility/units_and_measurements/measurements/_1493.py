'''_1493.py

TemperatureDifference
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_TEMPERATURE_DIFFERENCE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'TemperatureDifference')


__docformat__ = 'restructuredtext en'
__all__ = ('TemperatureDifference',)


class TemperatureDifference(_1398.MeasurementBase):
    '''TemperatureDifference

    This is a mastapy class.
    '''

    TYPE = _TEMPERATURE_DIFFERENCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TemperatureDifference.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
