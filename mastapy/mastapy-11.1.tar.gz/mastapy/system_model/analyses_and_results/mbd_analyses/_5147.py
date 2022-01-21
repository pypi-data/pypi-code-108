'''_5147.py

CVTPulleyMultibodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.couplings import _2327
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses import _5201
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'CVTPulleyMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyMultibodyDynamicsAnalysis',)


class CVTPulleyMultibodyDynamicsAnalysis(_5201.PulleyMultibodyDynamicsAnalysis):
    '''CVTPulleyMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2327.CVTPulley)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
