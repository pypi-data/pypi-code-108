'''_827.py

ConicalGearLoadDistributionAnalysis
'''


from mastapy.gears.ltca import _800
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalGearLoadDistributionAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearLoadDistributionAnalysis',)


class ConicalGearLoadDistributionAnalysis(_800.GearLoadDistributionAnalysis):
    '''ConicalGearLoadDistributionAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_LOAD_DISTRIBUTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearLoadDistributionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
