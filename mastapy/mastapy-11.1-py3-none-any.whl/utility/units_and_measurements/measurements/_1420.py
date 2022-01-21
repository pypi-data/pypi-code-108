'''_1420.py

DataSize
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_DATA_SIZE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'DataSize')


__docformat__ = 'restructuredtext en'
__all__ = ('DataSize',)


class DataSize(_1398.MeasurementBase):
    '''DataSize

    This is a mastapy class.
    '''

    TYPE = _DATA_SIZE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DataSize.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
