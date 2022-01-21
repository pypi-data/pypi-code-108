'''_1482.py

QuadraticAngularDamping
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_QUADRATIC_ANGULAR_DAMPING = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'QuadraticAngularDamping')


__docformat__ = 'restructuredtext en'
__all__ = ('QuadraticAngularDamping',)


class QuadraticAngularDamping(_1398.MeasurementBase):
    '''QuadraticAngularDamping

    This is a mastapy class.
    '''

    TYPE = _QUADRATIC_ANGULAR_DAMPING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'QuadraticAngularDamping.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
