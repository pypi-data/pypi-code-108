'''_1487.py

SpecificAcousticImpedance
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_SPECIFIC_ACOUSTIC_IMPEDANCE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'SpecificAcousticImpedance')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecificAcousticImpedance',)


class SpecificAcousticImpedance(_1398.MeasurementBase):
    '''SpecificAcousticImpedance

    This is a mastapy class.
    '''

    TYPE = _SPECIFIC_ACOUSTIC_IMPEDANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpecificAcousticImpedance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
