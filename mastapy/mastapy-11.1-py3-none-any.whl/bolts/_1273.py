'''_1273.py

ClampedSection
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import
from mastapy.bolts import _1264, _1268
from mastapy._internal.cast_exception import CastException
from mastapy import _0

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CLAMPED_SECTION = python_net_import('SMT.MastaAPI.Bolts', 'ClampedSection')


__docformat__ = 'restructuredtext en'
__all__ = ('ClampedSection',)


class ClampedSection(_0.APIBase):
    '''ClampedSection

    This is a mastapy class.
    '''

    TYPE = _CLAMPED_SECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ClampedSection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def part_thickness(self) -> 'float':
        '''float: 'PartThickness' is the original name of this property.'''

        return self.wrapped.PartThickness

    @part_thickness.setter
    def part_thickness(self, value: 'float'):
        self.wrapped.PartThickness = float(value) if value else 0.0

    @property
    def edit_material(self) -> 'str':
        '''str: 'EditMaterial' is the original name of this property.'''

        return self.wrapped.EditMaterial.SelectedItemName

    @edit_material.setter
    def edit_material(self, value: 'str'):
        self.wrapped.EditMaterial.SetSelectedItem(str(value) if value else '')

    @property
    def material(self) -> '_1264.BoltedJointMaterial':
        '''BoltedJointMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1264.BoltedJointMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to BoltedJointMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None
