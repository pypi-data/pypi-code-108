'''_1993.py

ModelViewOptionsDrawStyle
'''


from mastapy._internal import constructor
from mastapy.geometry import _275
from mastapy._internal.python_net import python_net_import

_MODEL_VIEW_OPTIONS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'ModelViewOptionsDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('ModelViewOptionsDrawStyle',)


class ModelViewOptionsDrawStyle(_275.DrawStyle):
    '''ModelViewOptionsDrawStyle

    This is a mastapy class.
    '''

    TYPE = _MODEL_VIEW_OPTIONS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModelViewOptionsDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def show_nodes(self) -> 'bool':
        '''bool: 'ShowNodes' is the original name of this property.'''

        return self.wrapped.ShowNodes

    @show_nodes.setter
    def show_nodes(self, value: 'bool'):
        self.wrapped.ShowNodes = bool(value) if value else False

    @property
    def solid_3d_shafts(self) -> 'bool':
        '''bool: 'Solid3DShafts' is the original name of this property.'''

        return self.wrapped.Solid3DShafts

    @solid_3d_shafts.setter
    def solid_3d_shafts(self, value: 'bool'):
        self.wrapped.Solid3DShafts = bool(value) if value else False

    @property
    def show_part_labels(self) -> 'bool':
        '''bool: 'ShowPartLabels' is the original name of this property.'''

        return self.wrapped.ShowPartLabels

    @show_part_labels.setter
    def show_part_labels(self, value: 'bool'):
        self.wrapped.ShowPartLabels = bool(value) if value else False

    @property
    def solid_components(self) -> 'bool':
        '''bool: 'SolidComponents' is the original name of this property.'''

        return self.wrapped.SolidComponents

    @solid_components.setter
    def solid_components(self, value: 'bool'):
        self.wrapped.SolidComponents = bool(value) if value else False

    @property
    def solid_housing(self) -> 'bool':
        '''bool: 'SolidHousing' is the original name of this property.'''

        return self.wrapped.SolidHousing

    @solid_housing.setter
    def solid_housing(self, value: 'bool'):
        self.wrapped.SolidHousing = bool(value) if value else False

    @property
    def rigid_elements(self) -> 'bool':
        '''bool: 'RigidElements' is the original name of this property.'''

        return self.wrapped.RigidElements

    @rigid_elements.setter
    def rigid_elements(self, value: 'bool'):
        self.wrapped.RigidElements = bool(value) if value else False

    @property
    def transparent_model(self) -> 'bool':
        '''bool: 'TransparentModel' is the original name of this property.'''

        return self.wrapped.TransparentModel

    @transparent_model.setter
    def transparent_model(self, value: 'bool'):
        self.wrapped.TransparentModel = bool(value) if value else False
