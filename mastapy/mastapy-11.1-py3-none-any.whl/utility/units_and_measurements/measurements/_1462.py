'''_1462.py

Mass
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_MASS = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Mass')


__docformat__ = 'restructuredtext en'
__all__ = ('Mass',)


class Mass(_1398.MeasurementBase):
    '''Mass

    This is a mastapy class.
    '''

    TYPE = _MASS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Mass.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
