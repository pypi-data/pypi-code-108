'''_207.py

StaticCMSResults
'''


from mastapy.nodal_analysis.states import _119, _118
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.nodal_analysis.component_mode_synthesis import _205
from mastapy._internal.python_net import python_net_import

_STATIC_CMS_RESULTS = python_net_import('SMT.MastaAPI.NodalAnalysis.ComponentModeSynthesis', 'StaticCMSResults')


__docformat__ = 'restructuredtext en'
__all__ = ('StaticCMSResults',)


class StaticCMSResults(_205.RealCMSResults):
    '''StaticCMSResults

    This is a mastapy class.
    '''

    TYPE = _STATIC_CMS_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StaticCMSResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def node_stress_tensors(self) -> '_119.NodeVectorState':
        '''NodeVectorState: 'NodeStressTensors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _119.NodeVectorState.TYPE not in self.wrapped.NodeStressTensors.__class__.__mro__:
            raise CastException('Failed to cast node_stress_tensors to NodeVectorState. Expected: {}.'.format(self.wrapped.NodeStressTensors.__class__.__qualname__))

        return constructor.new_override(self.wrapped.NodeStressTensors.__class__)(self.wrapped.NodeStressTensors) if self.wrapped.NodeStressTensors is not None else None

    def calculate_stress(self):
        ''' 'CalculateStress' is the original name of this method.'''

        self.wrapped.CalculateStress()
