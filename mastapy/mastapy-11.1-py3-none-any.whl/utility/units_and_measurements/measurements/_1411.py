'''_1411.py

AngularCompliance
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGULAR_COMPLIANCE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AngularCompliance')


__docformat__ = 'restructuredtext en'
__all__ = ('AngularCompliance',)


class AngularCompliance(_1398.MeasurementBase):
    '''AngularCompliance

    This is a mastapy class.
    '''

    TYPE = _ANGULAR_COMPLIANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngularCompliance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
