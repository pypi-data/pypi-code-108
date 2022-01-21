'''_4862.py

CVTModalAnalysis
'''


from mastapy.system_model.part_model.couplings import _2326
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.system_deflections import _2469
from mastapy.system_model.analyses_and_results.modal_analyses import _4830
from mastapy._internal.python_net import python_net_import

_CVT_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'CVTModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTModalAnalysis',)


class CVTModalAnalysis(_4830.BeltDriveModalAnalysis):
    '''CVTModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2326.CVT':
        '''CVT: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2326.CVT)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def system_deflection_results(self) -> '_2469.CVTSystemDeflection':
        '''CVTSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2469.CVTSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
