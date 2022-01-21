'''_3617.py

SynchroniserStabilityAnalysis
'''


from mastapy.system_model.part_model.couplings import _2342
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6687
from mastapy.system_model.analyses_and_results.stability_analyses import _3597
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'SynchroniserStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserStabilityAnalysis',)


class SynchroniserStabilityAnalysis(_3597.SpecialisedAssemblyStabilityAnalysis):
    '''SynchroniserStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2342.Synchroniser':
        '''Synchroniser: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2342.Synchroniser)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6687.SynchroniserLoadCase':
        '''SynchroniserLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6687.SynchroniserLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
