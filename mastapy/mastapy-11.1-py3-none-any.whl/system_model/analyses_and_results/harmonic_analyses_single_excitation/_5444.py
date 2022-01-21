'''_5444.py

CVTHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model.couplings import _2326
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5413
from mastapy._internal.python_net import python_net_import

_CVT_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'CVTHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTHarmonicAnalysisOfSingleExcitation',)


class CVTHarmonicAnalysisOfSingleExcitation(_5413.BeltDriveHarmonicAnalysisOfSingleExcitation):
    '''CVTHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _CVT_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2326.CVT':
        '''CVT: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2326.CVT)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None
