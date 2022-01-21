'''_2463.py

ConnectorSystemDeflection
'''


from typing import List

from mastapy._math.vector_3d import Vector3D
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import _2189, _2182, _2207
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.part_model.couplings import _2338
from mastapy.system_model.analyses_and_results.system_deflections import _2492, _2517
from mastapy.math_utility.measured_vectors import _1363
from mastapy.system_model.fe import _2126
from mastapy.system_model.analyses_and_results.power_flows import (
    _3801, _3773, _3844, _3863
)
from mastapy._internal.python_net import python_net_import

_CONNECTOR_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'ConnectorSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConnectorSystemDeflection',)


class ConnectorSystemDeflection(_2517.MountableComponentSystemDeflection):
    '''ConnectorSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConnectorSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def linear_force_on_inner(self) -> 'Vector3D':
        '''Vector3D: 'LinearForceOnInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.LinearForceOnInner)
        return value

    @property
    def moment_on_inner(self) -> 'Vector3D':
        '''Vector3D: 'MomentOnInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.MomentOnInner)
        return value

    @property
    def convergence_delta_energy(self) -> 'float':
        '''float: 'ConvergenceDeltaEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConvergenceDeltaEnergy

    @property
    def component_design(self) -> '_2189.Connector':
        '''Connector: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2189.Connector.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Connector. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_bearing(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2182.Bearing.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to Bearing. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_oil_seal(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2207.OilSeal.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to OilSeal. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_design_of_type_shaft_hub_connection(self) -> '_2338.ShaftHubConnection':
        '''ShaftHubConnection: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2338.ShaftHubConnection.TYPE not in self.wrapped.ComponentDesign.__class__.__mro__:
            raise CastException('Failed to cast component_design to ShaftHubConnection. Expected: {}.'.format(self.wrapped.ComponentDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ComponentDesign.__class__)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def outer_fe_part(self) -> '_2492.FEPartSystemDeflection':
        '''FEPartSystemDeflection: 'OuterFEPart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2492.FEPartSystemDeflection)(self.wrapped.OuterFEPart) if self.wrapped.OuterFEPart is not None else None

    @property
    def force_on_outer_support_in_wcs(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ForceOnOuterSupportInWCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ForceOnOuterSupportInWCS) if self.wrapped.ForceOnOuterSupportInWCS is not None else None

    @property
    def force_on_outer_support_in_lcs(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ForceOnOuterSupportInLCS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ForceOnOuterSupportInLCS) if self.wrapped.ForceOnOuterSupportInLCS is not None else None

    @property
    def outer_fe_substructure_nodes(self) -> 'List[_2126.FESubstructureNode]':
        '''List[FESubstructureNode]: 'OuterFESubstructureNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OuterFESubstructureNodes, constructor.new(_2126.FESubstructureNode))
        return value

    @property
    def power_flow_results(self) -> '_3801.ConnectorPowerFlow':
        '''ConnectorPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3801.ConnectorPowerFlow.TYPE not in self.wrapped.PowerFlowResults.__class__.__mro__:
            raise CastException('Failed to cast power_flow_results to ConnectorPowerFlow. Expected: {}.'.format(self.wrapped.PowerFlowResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PowerFlowResults.__class__)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def power_flow_results_of_type_bearing_power_flow(self) -> '_3773.BearingPowerFlow':
        '''BearingPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3773.BearingPowerFlow.TYPE not in self.wrapped.PowerFlowResults.__class__.__mro__:
            raise CastException('Failed to cast power_flow_results to BearingPowerFlow. Expected: {}.'.format(self.wrapped.PowerFlowResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PowerFlowResults.__class__)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def power_flow_results_of_type_oil_seal_power_flow(self) -> '_3844.OilSealPowerFlow':
        '''OilSealPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3844.OilSealPowerFlow.TYPE not in self.wrapped.PowerFlowResults.__class__.__mro__:
            raise CastException('Failed to cast power_flow_results to OilSealPowerFlow. Expected: {}.'.format(self.wrapped.PowerFlowResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PowerFlowResults.__class__)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def power_flow_results_of_type_shaft_hub_connection_power_flow(self) -> '_3863.ShaftHubConnectionPowerFlow':
        '''ShaftHubConnectionPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3863.ShaftHubConnectionPowerFlow.TYPE not in self.wrapped.PowerFlowResults.__class__.__mro__:
            raise CastException('Failed to cast power_flow_results to ShaftHubConnectionPowerFlow. Expected: {}.'.format(self.wrapped.PowerFlowResults.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PowerFlowResults.__class__)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None
