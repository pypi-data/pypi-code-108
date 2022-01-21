'''_5205.py

RollingRingConnectionMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy.system_model.connections_and_sockets import _2034
from mastapy.system_model.analyses_and_results.static_loads import _6664
from mastapy.system_model.analyses_and_results.mbd_analyses import _5175
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'RollingRingConnectionMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingConnectionMultibodyDynamicsAnalysis',)


class RollingRingConnectionMultibodyDynamicsAnalysis(_5175.InterMountableComponentConnectionMultibodyDynamicsAnalysis):
    '''RollingRingConnectionMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingConnectionMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def separation(self) -> 'float':
        '''float: 'Separation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Separation

    @property
    def normal_force(self) -> 'float':
        '''float: 'NormalForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalForce

    @property
    def force_on_ring_a(self) -> 'Vector3D':
        '''Vector3D: 'ForceOnRingA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ForceOnRingA)
        return value

    @property
    def connection_design(self) -> '_2034.RollingRingConnection':
        '''RollingRingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2034.RollingRingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6664.RollingRingConnectionLoadCase':
        '''RollingRingConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6664.RollingRingConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[RollingRingConnectionMultibodyDynamicsAnalysis]':
        '''List[RollingRingConnectionMultibodyDynamicsAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(RollingRingConnectionMultibodyDynamicsAnalysis))
        return value
