'''_828.py

ConicalGearSetLoadDistributionAnalysis
'''


from mastapy.gears.ltca import _806
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalGearSetLoadDistributionAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetLoadDistributionAnalysis',)


class ConicalGearSetLoadDistributionAnalysis(_806.GearSetLoadDistributionAnalysis):
    '''ConicalGearSetLoadDistributionAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_LOAD_DISTRIBUTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetLoadDistributionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
