'''_1445.py

InverseShortLength
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_INVERSE_SHORT_LENGTH = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'InverseShortLength')


__docformat__ = 'restructuredtext en'
__all__ = ('InverseShortLength',)


class InverseShortLength(_1398.MeasurementBase):
    '''InverseShortLength

    This is a mastapy class.
    '''

    TYPE = _INVERSE_SHORT_LENGTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InverseShortLength.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
