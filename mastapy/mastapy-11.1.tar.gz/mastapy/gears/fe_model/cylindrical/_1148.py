'''_1148.py

CylindricalGearFEModel
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.fe_model import _1144
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FE_MODEL = python_net_import('SMT.MastaAPI.Gears.FEModel.Cylindrical', 'CylindricalGearFEModel')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFEModel',)


class CylindricalGearFEModel(_1144.GearFEModel):
    '''CylindricalGearFEModel

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FE_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFEModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_specified_web(self) -> 'bool':
        '''bool: 'UseSpecifiedWeb' is the original name of this property.'''

        return self.wrapped.UseSpecifiedWeb

    @use_specified_web.setter
    def use_specified_web(self, value: 'bool'):
        self.wrapped.UseSpecifiedWeb = bool(value) if value else False

    @property
    def thickness_for_analyses(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'ThicknessForAnalyses' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.ThicknessForAnalyses) if self.wrapped.ThicknessForAnalyses is not None else None

    @thickness_for_analyses.setter
    def thickness_for_analyses(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.ThicknessForAnalyses = value
