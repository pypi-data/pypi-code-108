'''_1446.py

InverseShortTime
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_INVERSE_SHORT_TIME = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'InverseShortTime')


__docformat__ = 'restructuredtext en'
__all__ = ('InverseShortTime',)


class InverseShortTime(_1398.MeasurementBase):
    '''InverseShortTime

    This is a mastapy class.
    '''

    TYPE = _INVERSE_SHORT_TIME

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InverseShortTime.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
