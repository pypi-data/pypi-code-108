'''_2310.py

RingPins
'''


from mastapy._internal.python_net import python_net_import
from mastapy._internal import constructor
from mastapy.cycloidal import _1260, _1261
from mastapy.system_model.part_model import _2205

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_RING_PINS = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Cycloidal', 'RingPins')


__docformat__ = 'restructuredtext en'
__all__ = ('RingPins',)


class RingPins(_2205.MountableComponent):
    '''RingPins

    This is a mastapy class.
    '''

    TYPE = _RING_PINS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RingPins.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def ring_pins_material_database(self) -> 'str':
        '''str: 'RingPinsMaterialDatabase' is the original name of this property.'''

        return self.wrapped.RingPinsMaterialDatabase.SelectedItemName

    @ring_pins_material_database.setter
    def ring_pins_material_database(self, value: 'str'):
        self.wrapped.RingPinsMaterialDatabase.SetSelectedItem(str(value) if value else '')

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def ring_pins_design(self) -> '_1260.RingPinsDesign':
        '''RingPinsDesign: 'RingPinsDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1260.RingPinsDesign)(self.wrapped.RingPinsDesign) if self.wrapped.RingPinsDesign is not None else None

    @property
    def ring_pins_material(self) -> '_1261.RingPinsMaterial':
        '''RingPinsMaterial: 'RingPinsMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1261.RingPinsMaterial)(self.wrapped.RingPinsMaterial) if self.wrapped.RingPinsMaterial is not None else None
