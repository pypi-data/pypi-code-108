'''_1860.py

InnerRingFittingThermalResults
'''


from mastapy.bearings.bearing_results.rolling.fitting import _1863
from mastapy._internal.python_net import python_net_import

_INNER_RING_FITTING_THERMAL_RESULTS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.Fitting', 'InnerRingFittingThermalResults')


__docformat__ = 'restructuredtext en'
__all__ = ('InnerRingFittingThermalResults',)


class InnerRingFittingThermalResults(_1863.RingFittingThermalResults):
    '''InnerRingFittingThermalResults

    This is a mastapy class.
    '''

    TYPE = _INNER_RING_FITTING_THERMAL_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InnerRingFittingThermalResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
