'''_580.py

CylindricalManufacturedGearSetDutyCycle
'''


from mastapy.gears.rating.cylindrical import _427
from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical import _585
from mastapy.gears.analysis import _1174
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MANUFACTURED_GEAR_SET_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'CylindricalManufacturedGearSetDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalManufacturedGearSetDutyCycle',)


class CylindricalManufacturedGearSetDutyCycle(_1174.GearSetImplementationAnalysisDutyCycle):
    '''CylindricalManufacturedGearSetDutyCycle

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MANUFACTURED_GEAR_SET_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalManufacturedGearSetDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_427.CylindricalGearSetDutyCycleRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def manufacturing_configuration(self) -> '_585.CylindricalSetManufacturingConfig':
        '''CylindricalSetManufacturingConfig: 'ManufacturingConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_585.CylindricalSetManufacturingConfig)(self.wrapped.ManufacturingConfiguration) if self.wrapped.ManufacturingConfiguration is not None else None
