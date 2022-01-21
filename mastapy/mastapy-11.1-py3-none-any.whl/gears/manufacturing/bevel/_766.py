'''_766.py

PinionFinishMachineSettings
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.conical import _1118
from mastapy.gears import _286
from mastapy._internal.python_net import python_net_import

_PINION_FINISH_MACHINE_SETTINGS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'PinionFinishMachineSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('PinionFinishMachineSettings',)


class PinionFinishMachineSettings(_286.ConicalGearToothSurface):
    '''PinionFinishMachineSettings

    This is a mastapy class.
    '''

    TYPE = _PINION_FINISH_MACHINE_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PinionFinishMachineSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cutter_radius(self) -> 'float':
        '''float: 'CutterRadius' is the original name of this property.'''

        return self.wrapped.CutterRadius

    @cutter_radius.setter
    def cutter_radius(self, value: 'float'):
        self.wrapped.CutterRadius = float(value) if value else 0.0

    @property
    def pinion_cutter_blade_angle(self) -> 'float':
        '''float: 'PinionCutterBladeAngle' is the original name of this property.'''

        return self.wrapped.PinionCutterBladeAngle

    @pinion_cutter_blade_angle.setter
    def pinion_cutter_blade_angle(self, value: 'float'):
        self.wrapped.PinionCutterBladeAngle = float(value) if value else 0.0

    @property
    def blade_edge_radius(self) -> 'float':
        '''float: 'BladeEdgeRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BladeEdgeRadius

    @property
    def toprem_letter(self) -> '_1118.TopremLetter':
        '''TopremLetter: 'TopremLetter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.TopremLetter)
        return constructor.new(_1118.TopremLetter)(value) if value is not None else None

    @property
    def toprem_angle(self) -> 'float':
        '''float: 'TopremAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TopremAngle

    @property
    def toprem_length(self) -> 'float':
        '''float: 'TopremLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TopremLength

    @property
    def cc_angle(self) -> 'float':
        '''float: 'CCAngle' is the original name of this property.'''

        return self.wrapped.CCAngle

    @cc_angle.setter
    def cc_angle(self, value: 'float'):
        self.wrapped.CCAngle = float(value) if value else 0.0

    @property
    def ease_off_at_toe_root(self) -> 'float':
        '''float: 'EaseOffAtToeRoot' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EaseOffAtToeRoot

    @property
    def ease_off_at_toe_tip(self) -> 'float':
        '''float: 'EaseOffAtToeTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EaseOffAtToeTip

    @property
    def ease_off_at_heel_root(self) -> 'float':
        '''float: 'EaseOffAtHeelRoot' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EaseOffAtHeelRoot

    @property
    def ease_off_at_heel_tip(self) -> 'float':
        '''float: 'EaseOffAtHeelTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EaseOffAtHeelTip
