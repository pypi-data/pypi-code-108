'''_1512.py

Yank
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_YANK = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'Yank')


__docformat__ = 'restructuredtext en'
__all__ = ('Yank',)


class Yank(_1398.MeasurementBase):
    '''Yank

    This is a mastapy class.
    '''

    TYPE = _YANK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Yank.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
