'''_1862.py

OuterRingFittingThermalResults
'''


from mastapy.bearings.bearing_results.rolling.fitting import _1863
from mastapy._internal.python_net import python_net_import

_OUTER_RING_FITTING_THERMAL_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.Fitting', 'OuterRingFittingThermalResults')


__docformat__ = 'restructuredtext en'
__all__ = ('OuterRingFittingThermalResults',)


class OuterRingFittingThermalResults(_1863.RingFittingThermalResults):
    '''OuterRingFittingThermalResults

    This is a mastapy class.
    '''

    TYPE = _OUTER_RING_FITTING_THERMAL_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OuterRingFittingThermalResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
