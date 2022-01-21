'''_1412.py

AngularJerk
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGULAR_JERK = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AngularJerk')


__docformat__ = 'restructuredtext en'
__all__ = ('AngularJerk',)


class AngularJerk(_1398.MeasurementBase):
    '''AngularJerk

    This is a mastapy class.
    '''

    TYPE = _ANGULAR_JERK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngularJerk.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
