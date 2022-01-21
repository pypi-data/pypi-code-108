'''_1504.py

TorqueConverterK
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_K = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'TorqueConverterK')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterK',)


class TorqueConverterK(_1398.MeasurementBase):
    '''TorqueConverterK

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_K

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterK.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
