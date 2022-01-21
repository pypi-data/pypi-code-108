'''_1410.py

AngularAcceleration
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGULAR_ACCELERATION = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AngularAcceleration')


__docformat__ = 'restructuredtext en'
__all__ = ('AngularAcceleration',)


class AngularAcceleration(_1398.MeasurementBase):
    '''AngularAcceleration

    This is a mastapy class.
    '''

    TYPE = _ANGULAR_ACCELERATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngularAcceleration.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
