'''_6606.py

GearManufactureError
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'GearManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('GearManufactureError',)


class GearManufactureError(_0.APIBase):
    '''GearManufactureError

    This is a mastapy class.
    '''

    TYPE = _GEAR_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_custom_pitch_errors(self) -> 'bool':
        '''bool: 'UseCustomPitchErrors' is the original name of this property.'''

        return self.wrapped.UseCustomPitchErrors

    @use_custom_pitch_errors.setter
    def use_custom_pitch_errors(self, value: 'bool'):
        self.wrapped.UseCustomPitchErrors = bool(value) if value else False
