'''_446.py

ScuffingResultsRowGear
'''


from mastapy.gears.gear_designs.cylindrical import _981
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SCUFFING_RESULTS_ROW_GEAR = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical', 'ScuffingResultsRowGear')


__docformat__ = 'restructuredtext en'
__all__ = ('ScuffingResultsRowGear',)


class ScuffingResultsRowGear(_0.APIBase):
    '''ScuffingResultsRowGear

    This is a mastapy class.
    '''

    TYPE = _SCUFFING_RESULTS_ROW_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ScuffingResultsRowGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def profile_measurement(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ProfileMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ProfileMeasurement) if self.wrapped.ProfileMeasurement is not None else None
