'''_2132.py

FESubstructureWithSelectionComponents
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1298
from mastapy._math.vector_3d import Vector3D
from mastapy.system_model.fe.links import _2161
from mastapy.system_model.fe import (
    _2118, _2140, _2110, _2109,
    _2131
)
from mastapy.nodal_analysis.dev_tools_analyses.full_fe_reporting import (
    _185, _187, _186, _182,
    _188, _184, _183, _181
)
from mastapy._internal.python_net import python_net_import

_FE_SUBSTRUCTURE_WITH_SELECTION_COMPONENTS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FESubstructureWithSelectionComponents')


__docformat__ = 'restructuredtext en'
__all__ = ('FESubstructureWithSelectionComponents',)


class FESubstructureWithSelectionComponents(_2131.FESubstructureWithSelection):
    '''FESubstructureWithSelectionComponents

    This is a mastapy class.
    '''

    TYPE = _FE_SUBSTRUCTURE_WITH_SELECTION_COMPONENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FESubstructureWithSelectionComponents.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius_of_circle_through_selected_nodes(self) -> 'float':
        '''float: 'RadiusOfCircleThroughSelectedNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusOfCircleThroughSelectedNodes

    @property
    def manual_alignment(self) -> '_1298.CoordinateSystemEditor':
        '''CoordinateSystemEditor: 'ManualAlignment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1298.CoordinateSystemEditor)(self.wrapped.ManualAlignment) if self.wrapped.ManualAlignment is not None else None

    @property
    def distance_between_selected_nodes(self) -> 'Vector3D':
        '''Vector3D: 'DistanceBetweenSelectedNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.DistanceBetweenSelectedNodes)
        return value

    @property
    def midpoint_of_selected_nodes(self) -> 'Vector3D':
        '''Vector3D: 'MidpointOfSelectedNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.MidpointOfSelectedNodes)
        return value

    @property
    def centre_of_circle_through_selected_nodes(self) -> 'Vector3D':
        '''Vector3D: 'CentreOfCircleThroughSelectedNodes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.CentreOfCircleThroughSelectedNodes)
        return value

    @property
    def component_links(self) -> 'List[_2161.FELinkWithSelection]':
        '''List[FELinkWithSelection]: 'ComponentLinks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentLinks, constructor.new(_2161.FELinkWithSelection))
        return value

    @property
    def links_for_selected_component(self) -> 'List[_2161.FELinkWithSelection]':
        '''List[FELinkWithSelection]: 'LinksForSelectedComponent' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LinksForSelectedComponent, constructor.new(_2161.FELinkWithSelection))
        return value

    @property
    def links_for_electric_machine(self) -> 'List[_2161.FELinkWithSelection]':
        '''List[FELinkWithSelection]: 'LinksForElectricMachine' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LinksForElectricMachine, constructor.new(_2161.FELinkWithSelection))
        return value

    @property
    def rigid_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_185.ElementPropertiesRigid]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesRigid]]: 'RigidElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RigidElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_185.ElementPropertiesRigid])
        return value

    @property
    def solid_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_187.ElementPropertiesSolid]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesSolid]]: 'SolidElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SolidElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_187.ElementPropertiesSolid])
        return value

    @property
    def shell_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_186.ElementPropertiesShell]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesShell]]: 'ShellElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ShellElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_186.ElementPropertiesShell])
        return value

    @property
    def beam_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_182.ElementPropertiesBeam]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesBeam]]: 'BeamElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BeamElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_182.ElementPropertiesBeam])
        return value

    @property
    def spring_dashpot_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_188.ElementPropertiesSpringDashpot]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesSpringDashpot]]: 'SpringDashpotElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpringDashpotElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_188.ElementPropertiesSpringDashpot])
        return value

    @property
    def mass_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_184.ElementPropertiesMass]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesMass]]: 'MassElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MassElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_184.ElementPropertiesMass])
        return value

    @property
    def interface_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_183.ElementPropertiesInterface]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesInterface]]: 'InterfaceElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InterfaceElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_183.ElementPropertiesInterface])
        return value

    @property
    def other_element_properties(self) -> 'List[_2118.ElementPropertiesWithSelection[_181.ElementPropertiesBase]]':
        '''List[ElementPropertiesWithSelection[ElementPropertiesBase]]: 'OtherElementProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.OtherElementProperties, constructor.new(_2118.ElementPropertiesWithSelection)[_181.ElementPropertiesBase])
        return value

    @property
    def materials(self) -> 'List[_2140.MaterialPropertiesWithSelection]':
        '''List[MaterialPropertiesWithSelection]: 'Materials' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Materials, constructor.new(_2140.MaterialPropertiesWithSelection))
        return value

    @property
    def coordinate_systems(self) -> 'List[_2110.CoordinateSystemWithSelection]':
        '''List[CoordinateSystemWithSelection]: 'CoordinateSystems' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CoordinateSystems, constructor.new(_2110.CoordinateSystemWithSelection))
        return value

    @property
    def contact_pairs(self) -> 'List[_2109.ContactPairWithSelection]':
        '''List[ContactPairWithSelection]: 'ContactPairs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ContactPairs, constructor.new(_2109.ContactPairWithSelection))
        return value

    def replace_selected_shaft(self):
        ''' 'ReplaceSelectedShaft' is the original name of this method.'''

        self.wrapped.ReplaceSelectedShaft()

    def auto_select_node_ring(self):
        ''' 'AutoSelectNodeRing' is the original name of this method.'''

        self.wrapped.AutoSelectNodeRing()

    def use_selected_component_for_alignment(self):
        ''' 'UseSelectedComponentForAlignment' is the original name of this method.'''

        self.wrapped.UseSelectedComponentForAlignment()
