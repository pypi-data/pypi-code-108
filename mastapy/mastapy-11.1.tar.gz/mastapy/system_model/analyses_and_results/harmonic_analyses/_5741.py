'''_5741.py

GeneralPeriodicExcitationDetail
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import _5786
from mastapy._internal.python_net import python_net_import

_GENERAL_PERIODIC_EXCITATION_DETAIL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'GeneralPeriodicExcitationDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('GeneralPeriodicExcitationDetail',)


class GeneralPeriodicExcitationDetail(_5786.SingleNodePeriodicExcitationWithReferenceShaft):
    '''GeneralPeriodicExcitationDetail

    This is a mastapy class.
    '''

    TYPE = _GENERAL_PERIODIC_EXCITATION_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GeneralPeriodicExcitationDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
