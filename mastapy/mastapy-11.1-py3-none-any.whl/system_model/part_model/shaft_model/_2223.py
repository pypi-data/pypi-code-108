'''_2223.py

Shaft
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.part_model import (
    _2196, _2197, _2205, _2178
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import
from mastapy.shafts import _40
from mastapy.system_model.fe import _2124

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_SHAFT = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ShaftModel', 'Shaft')


__docformat__ = 'restructuredtext en'
__all__ = ('Shaft',)


class Shaft(_2178.AbstractShaft):
    '''Shaft

    This is a mastapy class.
    '''

    TYPE = _SHAFT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Shaft.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_replaced_by_fe(self) -> 'bool':
        '''bool: 'IsReplacedByFE' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsReplacedByFE

    @property
    def uses_cad_guide(self) -> 'bool':
        '''bool: 'UsesCADGuide' is the original name of this property.'''

        return self.wrapped.UsesCADGuide

    @uses_cad_guide.setter
    def uses_cad_guide(self, value: 'bool'):
        self.wrapped.UsesCADGuide = bool(value) if value else False

    @property
    def cad_model(self) -> 'list_with_selected_item.ListWithSelectedItem_GuideDxfModel':
        '''list_with_selected_item.ListWithSelectedItem_GuideDxfModel: 'CADModel' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_GuideDxfModel)(self.wrapped.CADModel) if self.wrapped.CADModel is not None else None

    @cad_model.setter
    def cad_model(self, value: 'list_with_selected_item.ListWithSelectedItem_GuideDxfModel.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_GuideDxfModel.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_GuideDxfModel.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.CADModel = value

    @property
    def has_guide_image(self) -> 'bool':
        '''bool: 'HasGuideImage' is the original name of this property.'''

        return self.wrapped.HasGuideImage

    @has_guide_image.setter
    def has_guide_image(self, value: 'bool'):
        self.wrapped.HasGuideImage = bool(value) if value else False

    @property
    def active_design(self) -> 'str':
        '''str: 'ActiveDesign' is the original name of this property.'''

        return self.wrapped.ActiveDesign.SelectedItemName

    @active_design.setter
    def active_design(self, value: 'str'):
        self.wrapped.ActiveDesign.SetSelectedItem(str(value) if value else '')

    @property
    def stress_to_yield_strength_factor(self) -> 'float':
        '''float: 'StressToYieldStrengthFactor' is the original name of this property.'''

        return self.wrapped.StressToYieldStrengthFactor

    @stress_to_yield_strength_factor.setter
    def stress_to_yield_strength_factor(self, value: 'float'):
        self.wrapped.StressToYieldStrengthFactor = float(value) if value else 0.0

    @property
    def position_fixed(self) -> 'bool':
        '''bool: 'PositionFixed' is the original name of this property.'''

        return self.wrapped.PositionFixed

    @position_fixed.setter
    def position_fixed(self, value: 'bool'):
        self.wrapped.PositionFixed = bool(value) if value else False

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def polar_inertia_of_shaft_body(self) -> 'float':
        '''float: 'PolarInertiaOfShaftBody' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PolarInertiaOfShaftBody

    @property
    def mass_of_shaft_body(self) -> 'float':
        '''float: 'MassOfShaftBody' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MassOfShaftBody

    @property
    def left_side_offset(self) -> 'float':
        '''float: 'LeftSideOffset' is the original name of this property.'''

        return self.wrapped.LeftSideOffset

    @left_side_offset.setter
    def left_side_offset(self, value: 'float'):
        self.wrapped.LeftSideOffset = float(value) if value else 0.0

    @property
    def rotation_about_axis_for_all_mounted_components(self) -> 'float':
        '''float: 'RotationAboutAxisForAllMountedComponents' is the original name of this property.'''

        return self.wrapped.RotationAboutAxisForAllMountedComponents

    @rotation_about_axis_for_all_mounted_components.setter
    def rotation_about_axis_for_all_mounted_components(self, value: 'float'):
        self.wrapped.RotationAboutAxisForAllMountedComponents = float(value) if value else 0.0

    @property
    def guide_image(self) -> '_2197.GuideImage':
        '''GuideImage: 'GuideImage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2197.GuideImage)(self.wrapped.GuideImage) if self.wrapped.GuideImage is not None else None

    @property
    def active_definition(self) -> '_40.SimpleShaftDefinition':
        '''SimpleShaftDefinition: 'ActiveDefinition' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_40.SimpleShaftDefinition)(self.wrapped.ActiveDefinition) if self.wrapped.ActiveDefinition is not None else None

    @property
    def fe_substructure_replacing_this(self) -> '_2124.FESubstructure':
        '''FESubstructure: 'FESubstructureReplacingThis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2124.FESubstructure)(self.wrapped.FESubstructureReplacingThis) if self.wrapped.FESubstructureReplacingThis is not None else None

    def cad_guide_alignment(self):
        ''' 'CADGuideAlignment' is the original name of this method.'''

        self.wrapped.CADGuideAlignment()

    def import_shaft(self):
        ''' 'ImportShaft' is the original name of this method.'''

        self.wrapped.ImportShaft()

    def remove_duplications(self):
        ''' 'RemoveDuplications' is the original name of this method.'''

        self.wrapped.RemoveDuplications()

    def remove_all_sections(self):
        ''' 'RemoveAllSections' is the original name of this method.'''

        self.wrapped.RemoveAllSections()

    def add_section(self, start_offset: 'float', end_offset: 'float', start_outer: 'float', start_inner: 'float', end_outer: 'float', end_inner: 'float'):
        ''' 'AddSection' is the original name of this method.

        Args:
            start_offset (float)
            end_offset (float)
            start_outer (float)
            start_inner (float)
            end_outer (float)
            end_inner (float)
        '''

        start_offset = float(start_offset)
        end_offset = float(end_offset)
        start_outer = float(start_outer)
        start_inner = float(start_inner)
        end_outer = float(end_outer)
        end_inner = float(end_inner)
        self.wrapped.AddSection(start_offset if start_offset else 0.0, end_offset if end_offset else 0.0, start_outer if start_outer else 0.0, start_inner if start_inner else 0.0, end_outer if end_outer else 0.0, end_inner if end_inner else 0.0)

    def mount_component(self, component: '_2205.MountableComponent', offset: 'float'):
        ''' 'MountComponent' is the original name of this method.

        Args:
            component (mastapy.system_model.part_model.MountableComponent)
            offset (float)
        '''

        offset = float(offset)
        self.wrapped.MountComponent(component.wrapped if component else None, offset if offset else 0.0)
