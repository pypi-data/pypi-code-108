'''_1463.py

MassPerUnitLength
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_MASS_PER_UNIT_LENGTH = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'MassPerUnitLength')


__docformat__ = 'restructuredtext en'
__all__ = ('MassPerUnitLength',)


class MassPerUnitLength(_1398.MeasurementBase):
    '''MassPerUnitLength

    This is a mastapy class.
    '''

    TYPE = _MASS_PER_UNIT_LENGTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassPerUnitLength.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
