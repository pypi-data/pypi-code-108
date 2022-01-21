'''_5786.py

SingleNodePeriodicExcitationWithReferenceShaft
'''


from mastapy.system_model.analyses_and_results.harmonic_analyses import _5770
from mastapy._internal.python_net import python_net_import

_SINGLE_NODE_PERIODIC_EXCITATION_WITH_REFERENCE_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'SingleNodePeriodicExcitationWithReferenceShaft')


__docformat__ = 'restructuredtext en'
__all__ = ('SingleNodePeriodicExcitationWithReferenceShaft',)


class SingleNodePeriodicExcitationWithReferenceShaft(_5770.PeriodicExcitationWithReferenceShaft):
    '''SingleNodePeriodicExcitationWithReferenceShaft

    This is a mastapy class.
    '''

    TYPE = _SINGLE_NODE_PERIODIC_EXCITATION_WITH_REFERENCE_SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingleNodePeriodicExcitationWithReferenceShaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
