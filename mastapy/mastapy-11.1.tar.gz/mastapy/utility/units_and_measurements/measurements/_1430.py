'''_1430.py

ForcePerUnitLength
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_FORCE_PER_UNIT_LENGTH = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'ForcePerUnitLength')


__docformat__ = 'restructuredtext en'
__all__ = ('ForcePerUnitLength',)


class ForcePerUnitLength(_1398.MeasurementBase):
    '''ForcePerUnitLength

    This is a mastapy class.
    '''

    TYPE = _FORCE_PER_UNIT_LENGTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ForcePerUnitLength.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
