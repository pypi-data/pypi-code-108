'''_1421.py

Decibel
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_DECIBEL = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Decibel')


__docformat__ = 'restructuredtext en'
__all__ = ('Decibel',)


class Decibel(_1398.MeasurementBase):
    '''Decibel

    This is a mastapy class.
    '''

    TYPE = _DECIBEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Decibel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
