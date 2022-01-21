'''_1465.py

MomentOfInertia
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_MOMENT_OF_INERTIA = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'MomentOfInertia')


__docformat__ = 'restructuredtext en'
__all__ = ('MomentOfInertia',)


class MomentOfInertia(_1398.MeasurementBase):
    '''MomentOfInertia

    This is a mastapy class.
    '''

    TYPE = _MOMENT_OF_INERTIA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MomentOfInertia.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
