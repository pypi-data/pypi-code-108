from typing import List

from pymint.constraints.constraint import LayoutConstraint
from pymint.mintcomponent import MINTComponent
from pymint.mintdevice import MINTDevice


class MirrorConstraint(LayoutConstraint):
    """Layout constraint when two differnt sub-netlists need to have
    the same layout
    """

    def __init__(self, source_component: MINTComponent, mirror_count=None):
        """Create a new instance of the mirror constraint

        Args:
            source_component (MINTComponent): source for the mirror component to search
            for mirror groups
            mirror_count ([type], optional): number of mirror groups. Defaults to None.
        """
        super().__init__()
        self.__mirror_source: MINTComponent = source_component
        self.__mirror_groups: List[List[MINTComponent]] = []
        self.__mirror_count: int = mirror_count

    def add_group(self, components: List[MINTComponent]) -> None:
        """Adds the passed componets to a new group

        Args:
            components (List[MINTComponent]): List of components that need to be in a
            mirror group
        """
        self.__mirror_groups.append(components)

    @property
    def mirror_source(self) -> MINTComponent:
        """Returns the mirror source component

        Returns:
            MINTComponent: mirror source
        """
        return self.__mirror_source

    @property
    def mirror_groups(self) -> List[List[MINTComponent]]:
        """Returns the mirror groups

        Returns:
            List[List[MINTComponent]]: Mirror groups covered by the constraint
        """
        return self.__mirror_groups

    def find_mirror_candidates(self, device: MINTDevice) -> None:
        """Traverses the device on the mirror groups

        Args:
            device (MINTDevice): device to traverse

        Raises:
            Exception: if component is not part of any group
        """
        forward_traverse = True
        # TODO -
        # Step 1 - Go through all the outgoing components and create create mirror
        # groups
        G = device.G
        mirror_groups = []

        outgoing_edges = list(G.out_edges(self.__mirror_source.ID))
        incoming_edges = list(G.in_edges(self.__mirror_source.ID))
        edges_to_use = None
        if len(outgoing_edges) == self.__mirror_count:
            forward_traverse = True
            edges_to_use = outgoing_edges
        elif len(incoming_edges) == self.__mirror_count:
            forward_traverse = False
            edges_to_use = incoming_edges
        else:
            # Reverse Case Considtion
            if len(incoming_edges) == self.__mirror_count:
                forward_traverse = True
                edges_to_use = outgoing_edges
            elif len(outgoing_edges) == self.__mirror_count:
                forward_traverse = False
                edges_to_use = incoming_edges
            else:
                raise Exception(
                    "Unable to compute mirror group for source: {}, please check if"
                    " outgoing and incoming channels are declared correctly".format(
                        self.__mirror_source
                    )
                )

        sources = []

        for i in range(self.__mirror_count):
            if forward_traverse is True:
                component = device.get_component(edges_to_use[i][1])
            else:
                component = device.get_component(edges_to_use[i][0])
            mirror_groups.append([component])
            sources.append(component.ID)

        if forward_traverse is True:
            self.step_forward(sources, mirror_groups, device)
        else:
            self.step_reverse(sources, mirror_groups, device)

        # Step 2 - Save teh mirror groups into our constraint object
        self.__mirror_groups = mirror_groups

    def step_forward(
        self,
        sources: List[str],
        mirror_groups: List[List[MINTComponent]],
        device: MINTDevice,
    ) -> bool:
        """Steps in the forward direction

        Args:
            sources (List[str]): [description]
            mirror_groups (List[List[MINTComponent]]): [description]
            device (MINTDevice): [description]

        Raises:
            Exception: [description]

        Returns:
            bool: [description]
        """
        G = device.G
        outgoing_edges = []
        for source in sources:
            outgoing_edges.extend(list(G.out_edges(source)))

        sink_ids = []
        for edge in list(outgoing_edges):
            sink_ids.append(edge[1])

        # If there is a only 1 common sink, or less than the mirror count, then we
        # gotto kill the mirror groupings
        if len(sink_ids) < self.__mirror_count:
            return False

        # Check if all the types of the components are the same
        entities = []
        components = []
        for id in sink_ids:
            component = device.get_component(id)
            entities.append(component.entity)
            components.append(component)

        # If all the entities are the same, include them into the mirror groups
        entity_0 = entities[0]
        fail_flag = False
        for i, unused_element in enumerate(sink_ids):
            entity_i = entities[i]
            if entity_i != entity_0:
                fail_flag = True

        if fail_flag is True:
            return False

        # Since it works, we add everything to the mirror groups, for each of the
        # components see which group the predecessor is in and place it in the
        # corresponding group, if its not in any of the groups something
        # went wrong in the alg
        for component in components:
            assing_group_found_flag = False
            for edge in list(G.in_edges(component.ID)):
                predecessor_component = device.get_component(edge[0])
                for group in mirror_groups:
                    if predecessor_component in group:
                        group.append(component)
                        assing_group_found_flag = True
                        break

            if assing_group_found_flag is False:
                raise Exception(
                    "Could not find the mirror group for component: {}".format(
                        component.ID
                    )
                )

        next_sources = [c.ID for c in components]
        # self.step_forward(next_sources, mirror_groups, device)

        return True

    def step_reverse(
        self,
        sources: List[str],
        mirror_groups: List[List[MINTComponent]],
        device: MINTDevice,
    ) -> bool:
        """Takes a step in reverse


        Args:
            sources (List[str]): [description]
            mirror_groups (List[List[MINTComponent]]): [description]
            device (MINTDevice): [description]

        Raises:
            Exception: [description]

        Returns:
            bool: [description]
        """
        G = device.G
        incoming_edges = []
        for source in sources:
            incoming_edges.extend(list(G.in_edges(source)))

        sink_ids = []
        for edge in list(incoming_edges):
            sink_ids.append(edge[0])

        # If there is a only 1 common sink, or less than the mirror count, then we
        # gotto kill the mirror groupings
        if len(sink_ids) < self.__mirror_count:
            return False

        # Check if all the types of the components are the same
        entities = []
        components = []
        for id in sink_ids:
            component = device.get_component(id)
            entities.append(component.entity)
            components.append(component)

        # If all the entities are the same, include them into the mirror groups
        entity_0 = entities[0]
        fail_flag = False
        for i, unused_element in enumerate(sink_ids):
            entity_i = entities[i]
            if entity_i != entity_0:
                fail_flag = True

        if fail_flag is True:
            return False

        # Since it works, we add everything to the mirror groups, for each of the
        # components see which group the predecessor is in and place it in the
        # corresponding group, if its not in any of the groups something
        # went wrong in the alg
        for component in components:
            assing_group_found_flag = False
            for edge in list(G.in_edges(component.ID)):
                predecessor_component = device.get_component(edge[0])
                for group in mirror_groups:
                    if predecessor_component in group:
                        group.append(component)
                        assing_group_found_flag = True
                        break

            if assing_group_found_flag is False:
                raise Exception(
                    "Could not find the mirror group for component: {}".format(
                        component.ID
                    )
                )

        next_sources = [c.ID for c in components]
        # self.step_forward(next_sources, mirror_groups, device)

        return True
