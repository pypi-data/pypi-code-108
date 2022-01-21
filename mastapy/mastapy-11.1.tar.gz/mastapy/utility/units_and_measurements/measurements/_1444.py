'''_1444.py

Integer
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_INTEGER = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Integer')


__docformat__ = 'restructuredtext en'
__all__ = ('Integer',)


class Integer(_1398.MeasurementBase):
    '''Integer

    This is a mastapy class.
    '''

    TYPE = _INTEGER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Integer.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
