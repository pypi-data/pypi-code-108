'''_2221.py

WindTurbineBladeModeDetails
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_WIND_TURBINE_BLADE_MODE_DETAILS = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'WindTurbineBladeModeDetails')


__docformat__ = 'restructuredtext en'
__all__ = ('WindTurbineBladeModeDetails',)


class WindTurbineBladeModeDetails(_0.APIBase):
    '''WindTurbineBladeModeDetails

    This is a mastapy class.
    '''

    TYPE = _WIND_TURBINE_BLADE_MODE_DETAILS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WindTurbineBladeModeDetails.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def inertia_of_hub(self) -> 'float':
        '''float: 'InertiaOfHub' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaOfHub

    @property
    def inertia_of_centre(self) -> 'float':
        '''float: 'InertiaOfCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaOfCentre

    @property
    def inertia_of_tip(self) -> 'float':
        '''float: 'InertiaOfTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaOfTip

    @property
    def stiffness_hub_to_centre(self) -> 'float':
        '''float: 'StiffnessHubToCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessHubToCentre

    @property
    def stiffness_centre_to_tip(self) -> 'float':
        '''float: 'StiffnessCentreToTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StiffnessCentreToTip

    @property
    def include_mode(self) -> 'bool':
        '''bool: 'IncludeMode' is the original name of this property.'''

        return self.wrapped.IncludeMode

    @include_mode.setter
    def include_mode(self, value: 'bool'):
        self.wrapped.IncludeMode = bool(value) if value else False

    @property
    def first_mode_frequency(self) -> 'float':
        '''float: 'FirstModeFrequency' is the original name of this property.'''

        return self.wrapped.FirstModeFrequency

    @first_mode_frequency.setter
    def first_mode_frequency(self, value: 'float'):
        self.wrapped.FirstModeFrequency = float(value) if value else 0.0

    @property
    def second_mode_frequency(self) -> 'float':
        '''float: 'SecondModeFrequency' is the original name of this property.'''

        return self.wrapped.SecondModeFrequency

    @second_mode_frequency.setter
    def second_mode_frequency(self, value: 'float'):
        self.wrapped.SecondModeFrequency = float(value) if value else 0.0
