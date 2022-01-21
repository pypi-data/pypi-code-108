'''_1413.py

AngularStiffness
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGULAR_STIFFNESS = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AngularStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('AngularStiffness',)


class AngularStiffness(_1398.MeasurementBase):
    '''AngularStiffness

    This is a mastapy class.
    '''

    TYPE = _ANGULAR_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngularStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
