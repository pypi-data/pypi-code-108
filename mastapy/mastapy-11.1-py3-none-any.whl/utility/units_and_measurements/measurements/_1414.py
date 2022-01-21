'''_1414.py

AngularVelocity
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGULAR_VELOCITY = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AngularVelocity')


__docformat__ = 'restructuredtext en'
__all__ = ('AngularVelocity',)


class AngularVelocity(_1398.MeasurementBase):
    '''AngularVelocity

    This is a mastapy class.
    '''

    TYPE = _ANGULAR_VELOCITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngularVelocity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
