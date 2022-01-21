'''_5218.py

SpringDamperConnectionMultibodyDynamicsAnalysis
'''


from mastapy._math.vector_3d import Vector3D
from mastapy._internal import constructor, conversion
from mastapy.system_model.connections_and_sockets.couplings import _2092
from mastapy.system_model.analyses_and_results.static_loads import _6675
from mastapy.system_model.analyses_and_results.mbd_analyses import _5142
from mastapy._internal.python_net import python_net_import

_SPRING_DAMPER_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'SpringDamperConnectionMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('SpringDamperConnectionMultibodyDynamicsAnalysis',)


class SpringDamperConnectionMultibodyDynamicsAnalysis(_5142.CouplingConnectionMultibodyDynamicsAnalysis):
    '''SpringDamperConnectionMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _SPRING_DAMPER_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpringDamperConnectionMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def force(self) -> 'Vector3D':
        '''Vector3D: 'Force' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Force)
        return value

    @property
    def moment(self) -> 'Vector3D':
        '''Vector3D: 'Moment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Moment)
        return value

    @property
    def relative_displacement(self) -> 'Vector3D':
        '''Vector3D: 'RelativeDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.RelativeDisplacement)
        return value

    @property
    def relative_rotation(self) -> 'Vector3D':
        '''Vector3D: 'RelativeRotation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.RelativeRotation)
        return value

    @property
    def connection_design(self) -> '_2092.SpringDamperConnection':
        '''SpringDamperConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2092.SpringDamperConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6675.SpringDamperConnectionLoadCase':
        '''SpringDamperConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6675.SpringDamperConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None
