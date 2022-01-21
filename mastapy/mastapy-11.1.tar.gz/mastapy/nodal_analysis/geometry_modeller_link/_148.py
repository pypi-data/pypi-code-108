'''_148.py

GeometryModellerSettings
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_GEOMETRY_MODELLER_SETTINGS = python_net_import('SMT.MastaAPI.NodalAnalysis.GeometryModellerLink', 'GeometryModellerSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('GeometryModellerSettings',)


class GeometryModellerSettings(_1387.PerMachineSettings):
    '''GeometryModellerSettings

    This is a mastapy class.
    '''

    TYPE = _GEOMETRY_MODELLER_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GeometryModellerSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_auto_detected_geometry_modeller_path(self) -> 'bool':
        '''bool: 'UseAutoDetectedGeometryModellerPath' is the original name of this property.'''

        return self.wrapped.UseAutoDetectedGeometryModellerPath

    @use_auto_detected_geometry_modeller_path.setter
    def use_auto_detected_geometry_modeller_path(self, value: 'bool'):
        self.wrapped.UseAutoDetectedGeometryModellerPath = bool(value) if value else False

    @property
    def auto_detected_geometry_modeller_path(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'AutoDetectedGeometryModellerPath' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.AutoDetectedGeometryModellerPath) if self.wrapped.AutoDetectedGeometryModellerPath is not None else None

    @auto_detected_geometry_modeller_path.setter
    def auto_detected_geometry_modeller_path(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.AutoDetectedGeometryModellerPath = value

    @property
    def geometry_modeller_arguments(self) -> 'str':
        '''str: 'GeometryModellerArguments' is the original name of this property.'''

        return self.wrapped.GeometryModellerArguments

    @geometry_modeller_arguments.setter
    def geometry_modeller_arguments(self, value: 'str'):
        self.wrapped.GeometryModellerArguments = str(value) if value else ''

    @property
    def disable_intel_mkl_internal_multithreading(self) -> 'bool':
        '''bool: 'DisableIntelMKLInternalMultithreading' is the original name of this property.'''

        return self.wrapped.DisableIntelMKLInternalMultithreading

    @disable_intel_mkl_internal_multithreading.setter
    def disable_intel_mkl_internal_multithreading(self, value: 'bool'):
        self.wrapped.DisableIntelMKLInternalMultithreading = bool(value) if value else False

    @property
    def folder_path(self) -> 'str':
        '''str: 'FolderPath' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FolderPath

    @property
    def hide_geometry_modeller_instead_of_closing(self) -> 'bool':
        '''bool: 'HideGeometryModellerInsteadOfClosing' is the original name of this property.'''

        return self.wrapped.HideGeometryModellerInsteadOfClosing

    @hide_geometry_modeller_instead_of_closing.setter
    def hide_geometry_modeller_instead_of_closing(self, value: 'bool'):
        self.wrapped.HideGeometryModellerInsteadOfClosing = bool(value) if value else False

    @property
    def show_message_when_hiding_geometry_modeller(self) -> 'bool':
        '''bool: 'ShowMessageWhenHidingGeometryModeller' is the original name of this property.'''

        return self.wrapped.ShowMessageWhenHidingGeometryModeller

    @show_message_when_hiding_geometry_modeller.setter
    def show_message_when_hiding_geometry_modeller(self, value: 'bool'):
        self.wrapped.ShowMessageWhenHidingGeometryModeller = bool(value) if value else False

    @property
    def no_licence_for_geometry_modeller(self) -> 'str':
        '''str: 'NoLicenceForGeometryModeller' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NoLicenceForGeometryModeller

    def select_folder_path(self):
        ''' 'SelectFolderPath' is the original name of this method.'''

        self.wrapped.SelectFolderPath()
