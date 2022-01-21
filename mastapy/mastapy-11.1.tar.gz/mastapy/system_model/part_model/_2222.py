'''_2222.py

WindTurbineSingleBladeDetails
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2221
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_WIND_TURBINE_SINGLE_BLADE_DETAILS = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'WindTurbineSingleBladeDetails')


__docformat__ = 'restructuredtext en'
__all__ = ('WindTurbineSingleBladeDetails',)


class WindTurbineSingleBladeDetails(_0.APIBase):
    '''WindTurbineSingleBladeDetails

    This is a mastapy class.
    '''

    TYPE = _WIND_TURBINE_SINGLE_BLADE_DETAILS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WindTurbineSingleBladeDetails.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mass_moment_of_inertia_about_hub(self) -> 'float':
        '''float: 'MassMomentOfInertiaAboutHub' is the original name of this property.'''

        return self.wrapped.MassMomentOfInertiaAboutHub

    @mass_moment_of_inertia_about_hub.setter
    def mass_moment_of_inertia_about_hub(self, value: 'float'):
        self.wrapped.MassMomentOfInertiaAboutHub = float(value) if value else 0.0

    @property
    def blade_length(self) -> 'float':
        '''float: 'BladeLength' is the original name of this property.'''

        return self.wrapped.BladeLength

    @blade_length.setter
    def blade_length(self, value: 'float'):
        self.wrapped.BladeLength = float(value) if value else 0.0

    @property
    def blade_drawing_length(self) -> 'float':
        '''float: 'BladeDrawingLength' is the original name of this property.'''

        return self.wrapped.BladeDrawingLength

    @blade_drawing_length.setter
    def blade_drawing_length(self, value: 'float'):
        self.wrapped.BladeDrawingLength = float(value) if value else 0.0

    @property
    def scale_blade_drawing_to_blade_drawing_length(self) -> 'bool':
        '''bool: 'ScaleBladeDrawingToBladeDrawingLength' is the original name of this property.'''

        return self.wrapped.ScaleBladeDrawingToBladeDrawingLength

    @scale_blade_drawing_to_blade_drawing_length.setter
    def scale_blade_drawing_to_blade_drawing_length(self, value: 'bool'):
        self.wrapped.ScaleBladeDrawingToBladeDrawingLength = bool(value) if value else False

    @property
    def blade_mass(self) -> 'float':
        '''float: 'BladeMass' is the original name of this property.'''

        return self.wrapped.BladeMass

    @blade_mass.setter
    def blade_mass(self, value: 'float'):
        self.wrapped.BladeMass = float(value) if value else 0.0

    @property
    def edgewise_modes(self) -> '_2221.WindTurbineBladeModeDetails':
        '''WindTurbineBladeModeDetails: 'EdgewiseModes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2221.WindTurbineBladeModeDetails)(self.wrapped.EdgewiseModes) if self.wrapped.EdgewiseModes is not None else None

    @property
    def flapwise_modes(self) -> '_2221.WindTurbineBladeModeDetails':
        '''WindTurbineBladeModeDetails: 'FlapwiseModes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2221.WindTurbineBladeModeDetails)(self.wrapped.FlapwiseModes) if self.wrapped.FlapwiseModes is not None else None
