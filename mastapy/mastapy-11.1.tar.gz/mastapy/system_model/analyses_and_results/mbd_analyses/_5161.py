'''_5161.py

FEPartMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import _2194
from mastapy.system_model.analyses_and_results.static_loads import _6602
from mastapy.system_model.analyses_and_results.mbd_analyses import _5104
from mastapy._internal.python_net import python_net_import

_FE_PART_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'FEPartMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('FEPartMultibodyDynamicsAnalysis',)


class FEPartMultibodyDynamicsAnalysis(_5104.AbstractShaftOrHousingMultibodyDynamicsAnalysis):
    '''FEPartMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _FE_PART_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEPartMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def elastic_local_x_deflections(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalXDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalXDeflections)
        return value

    @property
    def elastic_local_y_deflections(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalYDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalYDeflections)
        return value

    @property
    def elastic_local_z_deflections(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalZDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalZDeflections)
        return value

    @property
    def elastic_local_theta_x_deflections(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaXDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaXDeflections)
        return value

    @property
    def elastic_local_theta_y_deflections(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaYDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaYDeflections)
        return value

    @property
    def elastic_local_theta_z_deflections(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaZDeflections' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaZDeflections)
        return value

    @property
    def elastic_deflections_total_magnitude(self) -> 'List[float]':
        '''List[float]: 'ElasticDeflectionsTotalMagnitude' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticDeflectionsTotalMagnitude)
        return value

    @property
    def elastic_local_x_velocities(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalXVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalXVelocities)
        return value

    @property
    def elastic_local_y_velocities(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalYVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalYVelocities)
        return value

    @property
    def elastic_local_z_velocities(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalZVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalZVelocities)
        return value

    @property
    def elastic_local_theta_x_velocities(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaXVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaXVelocities)
        return value

    @property
    def elastic_local_theta_y_velocities(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaYVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaYVelocities)
        return value

    @property
    def elastic_local_theta_z_velocities(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaZVelocities' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaZVelocities)
        return value

    @property
    def elastic_local_x_accelerations(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalXAccelerations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalXAccelerations)
        return value

    @property
    def elastic_local_y_accelerations(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalYAccelerations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalYAccelerations)
        return value

    @property
    def elastic_local_z_accelerations(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalZAccelerations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalZAccelerations)
        return value

    @property
    def elastic_local_theta_x_accelerations(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaXAccelerations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaXAccelerations)
        return value

    @property
    def elastic_local_theta_y_accelerations(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaYAccelerations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaYAccelerations)
        return value

    @property
    def elastic_local_theta_z_accelerations(self) -> 'List[float]':
        '''List[float]: 'ElasticLocalThetaZAccelerations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.ElasticLocalThetaZAccelerations)
        return value

    @property
    def nodal_force_x(self) -> 'List[float]':
        '''List[float]: 'NodalForceX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodalForceX)
        return value

    @property
    def nodal_force_y(self) -> 'List[float]':
        '''List[float]: 'NodalForceY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodalForceY)
        return value

    @property
    def nodal_force_z(self) -> 'List[float]':
        '''List[float]: 'NodalForceZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodalForceZ)
        return value

    @property
    def nodal_force_theta_x(self) -> 'List[float]':
        '''List[float]: 'NodalForceThetaX' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodalForceThetaX)
        return value

    @property
    def nodal_force_theta_y(self) -> 'List[float]':
        '''List[float]: 'NodalForceThetaY' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodalForceThetaY)
        return value

    @property
    def nodal_force_theta_z(self) -> 'List[float]':
        '''List[float]: 'NodalForceThetaZ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_list_float(self.wrapped.NodalForceThetaZ)
        return value

    @property
    def component_design(self) -> '_2194.FEPart':
        '''FEPart: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2194.FEPart)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6602.FEPartLoadCase':
        '''FEPartLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6602.FEPartLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[FEPartMultibodyDynamicsAnalysis]':
        '''List[FEPartMultibodyDynamicsAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(FEPartMultibodyDynamicsAnalysis))
        return value
