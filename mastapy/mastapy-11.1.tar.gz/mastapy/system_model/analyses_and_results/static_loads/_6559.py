'''_6559.py

ConicalGearManufactureError
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1333
from mastapy.system_model.analyses_and_results.static_loads import _6606
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ConicalGearManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearManufactureError',)


class ConicalGearManufactureError(_6606.GearManufactureError):
    '''ConicalGearManufactureError

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pitch_error_phase_shift_on_concave_flank(self) -> 'float':
        '''float: 'PitchErrorPhaseShiftOnConcaveFlank' is the original name of this property.'''

        return self.wrapped.PitchErrorPhaseShiftOnConcaveFlank

    @pitch_error_phase_shift_on_concave_flank.setter
    def pitch_error_phase_shift_on_concave_flank(self, value: 'float'):
        self.wrapped.PitchErrorPhaseShiftOnConcaveFlank = float(value) if value else 0.0

    @property
    def pitch_error_phase_shift_on_convex_flank(self) -> 'float':
        '''float: 'PitchErrorPhaseShiftOnConvexFlank' is the original name of this property.'''

        return self.wrapped.PitchErrorPhaseShiftOnConvexFlank

    @pitch_error_phase_shift_on_convex_flank.setter
    def pitch_error_phase_shift_on_convex_flank(self, value: 'float'):
        self.wrapped.PitchErrorPhaseShiftOnConvexFlank = float(value) if value else 0.0

    @property
    def pitch_errors_concave_flank(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'PitchErrorsConcaveFlank' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.PitchErrorsConcaveFlank) if self.wrapped.PitchErrorsConcaveFlank is not None else None

    @pitch_errors_concave_flank.setter
    def pitch_errors_concave_flank(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.PitchErrorsConcaveFlank = value

    @property
    def pitch_errors_convex_flank(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'PitchErrorsConvexFlank' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.PitchErrorsConvexFlank) if self.wrapped.PitchErrorsConvexFlank is not None else None

    @pitch_errors_convex_flank.setter
    def pitch_errors_convex_flank(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.PitchErrorsConvexFlank = value
