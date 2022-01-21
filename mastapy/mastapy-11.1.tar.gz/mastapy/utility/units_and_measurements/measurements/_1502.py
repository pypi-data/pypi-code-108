'''_1502.py

Torque
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_TORQUE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Torque')


__docformat__ = 'restructuredtext en'
__all__ = ('Torque',)


class Torque(_1398.MeasurementBase):
    '''Torque

    This is a mastapy class.
    '''

    TYPE = _TORQUE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Torque.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
