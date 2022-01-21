'''_1500.py

TimeShort
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_TIME_SHORT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'TimeShort')


__docformat__ = 'restructuredtext en'
__all__ = ('TimeShort',)


class TimeShort(_1398.MeasurementBase):
    '''TimeShort

    This is a mastapy class.
    '''

    TYPE = _TIME_SHORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TimeShort.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
