'''_2211.py

PlanetCarrierSettings
'''


from mastapy.system_model import _1960
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_SETTINGS = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'PlanetCarrierSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierSettings',)


class PlanetCarrierSettings(_1387.PerMachineSettings):
    '''PlanetCarrierSettings

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planet_pin_manufacturing_errors_coordinate_system(self) -> '_1960.PlanetPinManufacturingErrorsCoordinateSystem':
        '''PlanetPinManufacturingErrorsCoordinateSystem: 'PlanetPinManufacturingErrorsCoordinateSystem' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.PlanetPinManufacturingErrorsCoordinateSystem)
        return constructor.new(_1960.PlanetPinManufacturingErrorsCoordinateSystem)(value) if value is not None else None

    @planet_pin_manufacturing_errors_coordinate_system.setter
    def planet_pin_manufacturing_errors_coordinate_system(self, value: '_1960.PlanetPinManufacturingErrorsCoordinateSystem'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.PlanetPinManufacturingErrorsCoordinateSystem = value
