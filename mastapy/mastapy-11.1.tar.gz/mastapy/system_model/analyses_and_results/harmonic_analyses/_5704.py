'''_5704.py

CVTBeltConnectionHarmonicAnalysis
'''


from mastapy.system_model.connections_and_sockets import _2015
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.system_deflections import _2467
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5672
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_HARMONIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'CVTBeltConnectionHarmonicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionHarmonicAnalysis',)


class CVTBeltConnectionHarmonicAnalysis(_5672.BeltConnectionHarmonicAnalysis):
    '''CVTBeltConnectionHarmonicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_HARMONIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionHarmonicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2015.CVTBeltConnection':
        '''CVTBeltConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2015.CVTBeltConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def system_deflection_results(self) -> '_2467.CVTBeltConnectionSystemDeflection':
        '''CVTBeltConnectionSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2467.CVTBeltConnectionSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
