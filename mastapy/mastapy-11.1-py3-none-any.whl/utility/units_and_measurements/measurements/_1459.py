'''_1459.py

LinearDamping
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LINEAR_DAMPING = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LinearDamping')


__docformat__ = 'restructuredtext en'
__all__ = ('LinearDamping',)


class LinearDamping(_1398.MeasurementBase):
    '''LinearDamping

    This is a mastapy class.
    '''

    TYPE = _LINEAR_DAMPING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LinearDamping.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
