'''_2189.py

Connector
'''


from typing import Optional

from mastapy.system_model.connections_and_sockets import (
    _2018, _2008, _2009, _2016,
    _2021, _2022, _2024, _2025,
    _2026, _2027, _2028, _2030,
    _2031, _2032, _2035, _2036,
    _2014, _2007, _2010, _2011,
    _2015, _2023, _2029, _2034,
    _2037
)
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.connections_and_sockets.gears import (
    _2052, _2041, _2043, _2045,
    _2047, _2049, _2051, _2053,
    _2055, _2057, _2060, _2061,
    _2062, _2065, _2067, _2069,
    _2071, _2073
)
from mastapy.system_model.connections_and_sockets.cycloidal import (
    _2075, _2076, _2078, _2079,
    _2081, _2082, _2077, _2080,
    _2083
)
from mastapy.system_model.connections_and_sockets.couplings import (
    _2085, _2087, _2089, _2091,
    _2093, _2095, _2096, _2084,
    _2086, _2088, _2090, _2092,
    _2094
)
from mastapy.system_model.part_model import (
    _2178, _2187, _2186, _2205
)
from mastapy.system_model.part_model.shaft_model import _2223
from mastapy.system_model.part_model.cycloidal import _2309
from mastapy._internal.python_net import python_net_import

_CONNECTOR = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'Connector')


__docformat__ = 'restructuredtext en'
__all__ = ('Connector',)


class Connector(_2205.MountableComponent):
    '''Connector

    This is a mastapy class.
    '''

    TYPE = _CONNECTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Connector.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def outer_socket(self) -> '_2018.CylindricalSocket':
        '''CylindricalSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2018.CylindricalSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CylindricalSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_bearing_inner_socket(self) -> '_2008.BearingInnerSocket':
        '''BearingInnerSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2008.BearingInnerSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to BearingInnerSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_bearing_outer_socket(self) -> '_2009.BearingOuterSocket':
        '''BearingOuterSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2009.BearingOuterSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to BearingOuterSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cvt_pulley_socket(self) -> '_2016.CVTPulleySocket':
        '''CVTPulleySocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2016.CVTPulleySocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CVTPulleySocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_inner_shaft_socket(self) -> '_2021.InnerShaftSocket':
        '''InnerShaftSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2021.InnerShaftSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to InnerShaftSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_inner_shaft_socket_base(self) -> '_2022.InnerShaftSocketBase':
        '''InnerShaftSocketBase: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2022.InnerShaftSocketBase.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to InnerShaftSocketBase. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_mountable_component_inner_socket(self) -> '_2024.MountableComponentInnerSocket':
        '''MountableComponentInnerSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2024.MountableComponentInnerSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to MountableComponentInnerSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_mountable_component_outer_socket(self) -> '_2025.MountableComponentOuterSocket':
        '''MountableComponentOuterSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2025.MountableComponentOuterSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to MountableComponentOuterSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_mountable_component_socket(self) -> '_2026.MountableComponentSocket':
        '''MountableComponentSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2026.MountableComponentSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to MountableComponentSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_outer_shaft_socket(self) -> '_2027.OuterShaftSocket':
        '''OuterShaftSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2027.OuterShaftSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to OuterShaftSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_outer_shaft_socket_base(self) -> '_2028.OuterShaftSocketBase':
        '''OuterShaftSocketBase: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2028.OuterShaftSocketBase.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to OuterShaftSocketBase. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_planetary_socket(self) -> '_2030.PlanetarySocket':
        '''PlanetarySocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2030.PlanetarySocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to PlanetarySocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_planetary_socket_base(self) -> '_2031.PlanetarySocketBase':
        '''PlanetarySocketBase: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2031.PlanetarySocketBase.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to PlanetarySocketBase. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_pulley_socket(self) -> '_2032.PulleySocket':
        '''PulleySocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2032.PulleySocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to PulleySocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_rolling_ring_socket(self) -> '_2035.RollingRingSocket':
        '''RollingRingSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2035.RollingRingSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to RollingRingSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_shaft_socket(self) -> '_2036.ShaftSocket':
        '''ShaftSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2036.ShaftSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to ShaftSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cylindrical_gear_teeth_socket(self) -> '_2052.CylindricalGearTeethSocket':
        '''CylindricalGearTeethSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2052.CylindricalGearTeethSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CylindricalGearTeethSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cycloidal_disc_axial_left_socket(self) -> '_2075.CycloidalDiscAxialLeftSocket':
        '''CycloidalDiscAxialLeftSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2075.CycloidalDiscAxialLeftSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CycloidalDiscAxialLeftSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cycloidal_disc_axial_right_socket(self) -> '_2076.CycloidalDiscAxialRightSocket':
        '''CycloidalDiscAxialRightSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2076.CycloidalDiscAxialRightSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CycloidalDiscAxialRightSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cycloidal_disc_inner_socket(self) -> '_2078.CycloidalDiscInnerSocket':
        '''CycloidalDiscInnerSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2078.CycloidalDiscInnerSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CycloidalDiscInnerSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cycloidal_disc_outer_socket(self) -> '_2079.CycloidalDiscOuterSocket':
        '''CycloidalDiscOuterSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2079.CycloidalDiscOuterSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CycloidalDiscOuterSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_cycloidal_disc_planetary_bearing_socket(self) -> '_2081.CycloidalDiscPlanetaryBearingSocket':
        '''CycloidalDiscPlanetaryBearingSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2081.CycloidalDiscPlanetaryBearingSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CycloidalDiscPlanetaryBearingSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_ring_pins_socket(self) -> '_2082.RingPinsSocket':
        '''RingPinsSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2082.RingPinsSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to RingPinsSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_clutch_socket(self) -> '_2085.ClutchSocket':
        '''ClutchSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2085.ClutchSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to ClutchSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_concept_coupling_socket(self) -> '_2087.ConceptCouplingSocket':
        '''ConceptCouplingSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2087.ConceptCouplingSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to ConceptCouplingSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_coupling_socket(self) -> '_2089.CouplingSocket':
        '''CouplingSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2089.CouplingSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to CouplingSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_part_to_part_shear_coupling_socket(self) -> '_2091.PartToPartShearCouplingSocket':
        '''PartToPartShearCouplingSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2091.PartToPartShearCouplingSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to PartToPartShearCouplingSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_spring_damper_socket(self) -> '_2093.SpringDamperSocket':
        '''SpringDamperSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2093.SpringDamperSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to SpringDamperSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_torque_converter_pump_socket(self) -> '_2095.TorqueConverterPumpSocket':
        '''TorqueConverterPumpSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2095.TorqueConverterPumpSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to TorqueConverterPumpSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_socket_of_type_torque_converter_turbine_socket(self) -> '_2096.TorqueConverterTurbineSocket':
        '''TorqueConverterTurbineSocket: 'OuterSocket' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2096.TorqueConverterTurbineSocket.TYPE not in self.wrapped.OuterSocket.__class__.__mro__:
            raise CastException('Failed to cast outer_socket to TorqueConverterTurbineSocket. Expected: {}.'.format(self.wrapped.OuterSocket.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterSocket.__class__)(self.wrapped.OuterSocket) if self.wrapped.OuterSocket is not None else None

    @property
    def outer_connection(self) -> '_2014.Connection':
        '''Connection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2014.Connection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to Connection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_abstract_shaft_to_mountable_component_connection(self) -> '_2007.AbstractShaftToMountableComponentConnection':
        '''AbstractShaftToMountableComponentConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2007.AbstractShaftToMountableComponentConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to AbstractShaftToMountableComponentConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_belt_connection(self) -> '_2010.BeltConnection':
        '''BeltConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2010.BeltConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to BeltConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_coaxial_connection(self) -> '_2011.CoaxialConnection':
        '''CoaxialConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2011.CoaxialConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to CoaxialConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_cvt_belt_connection(self) -> '_2015.CVTBeltConnection':
        '''CVTBeltConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2015.CVTBeltConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to CVTBeltConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_inter_mountable_component_connection(self) -> '_2023.InterMountableComponentConnection':
        '''InterMountableComponentConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2023.InterMountableComponentConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to InterMountableComponentConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_planetary_connection(self) -> '_2029.PlanetaryConnection':
        '''PlanetaryConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2029.PlanetaryConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to PlanetaryConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_rolling_ring_connection(self) -> '_2034.RollingRingConnection':
        '''RollingRingConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2034.RollingRingConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to RollingRingConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_shaft_to_mountable_component_connection(self) -> '_2037.ShaftToMountableComponentConnection':
        '''ShaftToMountableComponentConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2037.ShaftToMountableComponentConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to ShaftToMountableComponentConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_agma_gleason_conical_gear_mesh(self) -> '_2041.AGMAGleasonConicalGearMesh':
        '''AGMAGleasonConicalGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2041.AGMAGleasonConicalGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to AGMAGleasonConicalGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_bevel_differential_gear_mesh(self) -> '_2043.BevelDifferentialGearMesh':
        '''BevelDifferentialGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2043.BevelDifferentialGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to BevelDifferentialGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_bevel_gear_mesh(self) -> '_2045.BevelGearMesh':
        '''BevelGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2045.BevelGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to BevelGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_concept_gear_mesh(self) -> '_2047.ConceptGearMesh':
        '''ConceptGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2047.ConceptGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to ConceptGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_conical_gear_mesh(self) -> '_2049.ConicalGearMesh':
        '''ConicalGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2049.ConicalGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to ConicalGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_cylindrical_gear_mesh(self) -> '_2051.CylindricalGearMesh':
        '''CylindricalGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2051.CylindricalGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to CylindricalGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_face_gear_mesh(self) -> '_2053.FaceGearMesh':
        '''FaceGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2053.FaceGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to FaceGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_gear_mesh(self) -> '_2055.GearMesh':
        '''GearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2055.GearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to GearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_hypoid_gear_mesh(self) -> '_2057.HypoidGearMesh':
        '''HypoidGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2057.HypoidGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to HypoidGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_klingelnberg_cyclo_palloid_conical_gear_mesh(self) -> '_2060.KlingelnbergCycloPalloidConicalGearMesh':
        '''KlingelnbergCycloPalloidConicalGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2060.KlingelnbergCycloPalloidConicalGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to KlingelnbergCycloPalloidConicalGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_klingelnberg_cyclo_palloid_hypoid_gear_mesh(self) -> '_2061.KlingelnbergCycloPalloidHypoidGearMesh':
        '''KlingelnbergCycloPalloidHypoidGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2061.KlingelnbergCycloPalloidHypoidGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to KlingelnbergCycloPalloidHypoidGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(self) -> '_2062.KlingelnbergCycloPalloidSpiralBevelGearMesh':
        '''KlingelnbergCycloPalloidSpiralBevelGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2062.KlingelnbergCycloPalloidSpiralBevelGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to KlingelnbergCycloPalloidSpiralBevelGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_spiral_bevel_gear_mesh(self) -> '_2065.SpiralBevelGearMesh':
        '''SpiralBevelGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2065.SpiralBevelGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to SpiralBevelGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_straight_bevel_diff_gear_mesh(self) -> '_2067.StraightBevelDiffGearMesh':
        '''StraightBevelDiffGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2067.StraightBevelDiffGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to StraightBevelDiffGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_straight_bevel_gear_mesh(self) -> '_2069.StraightBevelGearMesh':
        '''StraightBevelGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2069.StraightBevelGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to StraightBevelGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_worm_gear_mesh(self) -> '_2071.WormGearMesh':
        '''WormGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2071.WormGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to WormGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_zerol_bevel_gear_mesh(self) -> '_2073.ZerolBevelGearMesh':
        '''ZerolBevelGearMesh: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2073.ZerolBevelGearMesh.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to ZerolBevelGearMesh. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_cycloidal_disc_central_bearing_connection(self) -> '_2077.CycloidalDiscCentralBearingConnection':
        '''CycloidalDiscCentralBearingConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2077.CycloidalDiscCentralBearingConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to CycloidalDiscCentralBearingConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_cycloidal_disc_planetary_bearing_connection(self) -> '_2080.CycloidalDiscPlanetaryBearingConnection':
        '''CycloidalDiscPlanetaryBearingConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2080.CycloidalDiscPlanetaryBearingConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to CycloidalDiscPlanetaryBearingConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_ring_pins_to_disc_connection(self) -> '_2083.RingPinsToDiscConnection':
        '''RingPinsToDiscConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2083.RingPinsToDiscConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to RingPinsToDiscConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_clutch_connection(self) -> '_2084.ClutchConnection':
        '''ClutchConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2084.ClutchConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to ClutchConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_concept_coupling_connection(self) -> '_2086.ConceptCouplingConnection':
        '''ConceptCouplingConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2086.ConceptCouplingConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to ConceptCouplingConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_coupling_connection(self) -> '_2088.CouplingConnection':
        '''CouplingConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2088.CouplingConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to CouplingConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_part_to_part_shear_coupling_connection(self) -> '_2090.PartToPartShearCouplingConnection':
        '''PartToPartShearCouplingConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2090.PartToPartShearCouplingConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to PartToPartShearCouplingConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_spring_damper_connection(self) -> '_2092.SpringDamperConnection':
        '''SpringDamperConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2092.SpringDamperConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to SpringDamperConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_connection_of_type_torque_converter_connection(self) -> '_2094.TorqueConverterConnection':
        '''TorqueConverterConnection: 'OuterConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2094.TorqueConverterConnection.TYPE not in self.wrapped.OuterConnection.__class__.__mro__:
            raise CastException('Failed to cast outer_connection to TorqueConverterConnection. Expected: {}.'.format(self.wrapped.OuterConnection.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterConnection.__class__)(self.wrapped.OuterConnection) if self.wrapped.OuterConnection is not None else None

    @property
    def outer_component(self) -> '_2178.AbstractShaft':
        '''AbstractShaft: 'OuterComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2178.AbstractShaft.TYPE not in self.wrapped.OuterComponent.__class__.__mro__:
            raise CastException('Failed to cast outer_component to AbstractShaft. Expected: {}.'.format(self.wrapped.OuterComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterComponent.__class__)(self.wrapped.OuterComponent) if self.wrapped.OuterComponent is not None else None

    @property
    def outer_component_of_type_shaft(self) -> '_2223.Shaft':
        '''Shaft: 'OuterComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2223.Shaft.TYPE not in self.wrapped.OuterComponent.__class__.__mro__:
            raise CastException('Failed to cast outer_component to Shaft. Expected: {}.'.format(self.wrapped.OuterComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterComponent.__class__)(self.wrapped.OuterComponent) if self.wrapped.OuterComponent is not None else None

    @property
    def outer_component_of_type_cycloidal_disc(self) -> '_2309.CycloidalDisc':
        '''CycloidalDisc: 'OuterComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2309.CycloidalDisc.TYPE not in self.wrapped.OuterComponent.__class__.__mro__:
            raise CastException('Failed to cast outer_component to CycloidalDisc. Expected: {}.'.format(self.wrapped.OuterComponent.__class__.__qualname__))

        return constructor.new_override(self.wrapped.OuterComponent.__class__)(self.wrapped.OuterComponent) if self.wrapped.OuterComponent is not None else None

    def house_in(self, shaft: '_2178.AbstractShaft', offset: Optional['float'] = float('nan')) -> '_2014.Connection':
        ''' 'HouseIn' is the original name of this method.

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)

        Returns:
            mastapy.system_model.connections_and_sockets.Connection
        '''

        offset = float(offset)
        method_result = self.wrapped.HouseIn(shaft.wrapped if shaft else None, offset if offset else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def try_house_in(self, shaft: '_2178.AbstractShaft', offset: Optional['float'] = float('nan')) -> '_2187.ComponentsConnectedResult':
        ''' 'TryHouseIn' is the original name of this method.

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)

        Returns:
            mastapy.system_model.part_model.ComponentsConnectedResult
        '''

        offset = float(offset)
        method_result = self.wrapped.TryHouseIn(shaft.wrapped if shaft else None, offset if offset else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def other_component(self, component: '_2186.Component') -> '_2178.AbstractShaft':
        ''' 'OtherComponent' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.Component)

        Returns:
            mastapy.system_model.part_model.AbstractShaft
        '''

        method_result = self.wrapped.OtherComponent(component.wrapped if component else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
