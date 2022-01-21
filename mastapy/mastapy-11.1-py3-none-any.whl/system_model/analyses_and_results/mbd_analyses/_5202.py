'''_5202.py

RingPinsMultibodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.cycloidal import _2310
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6661
from mastapy.system_model.analyses_and_results.mbd_analyses import _5190
from mastapy._internal.python_net import python_net_import

_RING_PINS_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'RingPinsMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPinsMultibodyDynamicsAnalysis',)


class RingPinsMultibodyDynamicsAnalysis(_5190.MountableComponentMultibodyDynamicsAnalysis):
    '''RingPinsMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _RING_PINS_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPinsMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2310.RingPins':
        '''RingPins: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2310.RingPins)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6661.RingPinsLoadCase':
        '''RingPinsLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6661.RingPinsLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
