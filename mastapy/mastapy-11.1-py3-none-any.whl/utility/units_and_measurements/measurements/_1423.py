'''_1423.py

Energy
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ENERGY = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Energy')


__docformat__ = 'restructuredtext en'
__all__ = ('Energy',)


class Energy(_1398.MeasurementBase):
    '''Energy

    This is a mastapy class.
    '''

    TYPE = _ENERGY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Energy.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
