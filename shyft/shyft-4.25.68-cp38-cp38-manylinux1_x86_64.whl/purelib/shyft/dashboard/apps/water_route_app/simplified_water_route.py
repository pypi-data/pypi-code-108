import itertools

from shyft.energy_market import stm
from shyft.util.layoutgraph import WaterRouteGraph, ghost_object_factory


class SimplifiedWaterRouteGraph(WaterRouteGraph):
    @staticmethod
    def get_next_node_downstream(obj: stm.Waterway):
        while obj.downstream:
            if isinstance(obj.downstream, stm.Waterway):
                obj = obj.downstream
            else:
                return obj.downstream
        return None

    def generate_graph(self, water_course: stm.HydroPowerSystem):
        """

        Parameters
        ----------
        water_course

        Returns
        -------

        """
        self.dh_tag_obj['reservoirs'] = {res.tag: res for res in water_course.reservoirs}
        self.dh_tag_obj['power_stations'] = {ps.tag: ps for ps in water_course.power_stations}

        self.dh_tag_obj['main_water_routes'] = {ww.tag: ww for ww in water_course.waterways if ww.upstream_role.name == 'main'}
        self.dh_tag_obj['spill_routes'] = {ww.tag: ww for ww in water_course.waterways if ww.upstream_role.name =='flood'}
        self.dh_tag_obj['bypass_routes'] = {ww.tag: ww for ww in water_course.waterways if ww.upstream_role.name =='bypass'}

        # 1. prepare all objects to be added and evaluate graph structure
        # 1.1 reservoirs and power stations
        node_objects = list(itertools.chain(self.dh_tag_obj['reservoirs'].values(),
                                            self.dh_tag_obj['power_stations'].values()))
        # 1.2 all water_routes
        all_edge_objects = list(itertools.chain(self.dh_tag_obj['main_water_routes'].values(),
                                                self.dh_tag_obj['spill_routes'].values(),
                                                self.dh_tag_obj['bypass_routes'].values()))

        object_layout_keys = ['Reservoir']*len(self.dh_tag_obj['reservoirs'])
        object_layout_keys.extend(['PowerStation'] * len(self.dh_tag_obj['power_stations']))

        # check if extra nodes are needed to add, and define start and end node lists
        start_objects = []
        edge_objects = []
        end_objects = []
        oceans = []
        ocean_counter = 0
        spill_oceans = []
        spill_ocean_cluster = []
        spill_ocean_config = []

        connections_dict = {}

        for i, obj in enumerate(all_edge_objects):
            # check for ocean and number of connections

            # connection to ocean
            if not isinstance(obj.upstream, stm.Waterway):
                node_upstream = obj.upstream
                if isinstance(node_upstream, stm.Unit):
                    node_upstream = node_upstream.power_plant
                node_downstream = self.get_next_node_downstream(obj)
                if not node_downstream:  # Reached the ocean
                    ocean_counter += 1
                    ocean = ghost_object_factory('Ocean', f"Ocean_{obj.tag}_{ocean_counter}")
                    node_downstream = ocean
                    if obj.upstream_role.name == 'main':
                        oceans.append(ocean)
                        self.dh_tag_obj['oceans'][ocean.tag] = ocean
                    else:
                        spill_ocean_cluster.append(ghost_object_factory('GraphSpillOcean',
                                                                        f'Spill_Ocean_Cluster_{ocean_counter}'))
                        spill_oceans.append([obj.upstreams[0].target, ocean])
                        self.dh_tag_obj[f'oceans_{obj.upstream_role.name}'][ocean.tag] = ocean

                        config_key = obj.upstreams[0].target.__class__.__name__
                        spill_ocean_config.append([config_key, 'OceanSpill'])
                if isinstance(node_downstream, stm.Unit):
                    node_downstream = node_downstream.power_plant
                start_objects.append(node_upstream)
                edge_objects.append(obj)
                end_objects.append(node_downstream)

        # 2. Add all objects to the graph
        # 2.1 Add all containers/nodes
        self.add_container(node_objects, object_layout_keys)

        # 2.2 Define all subgraphs (forced horizontal alignment)
        # create ocean subgraph
        ocean_subgraph_obj = ghost_object_factory('GraphOcean', 'Ocean_Subgraph')
        ocean_subgraph = self.add_subgraph(ocean_subgraph_obj, 'GraphOcean')
        # add containers to the ocean subgraph
        ocean_subgraph.add_container(oceans, ['Ocean']*len(oceans))

        # 2.3 Define all subgraphs (forced vertical alignment)
        for cluster_obj, node_objects, config in zip(spill_ocean_cluster, spill_oceans, spill_ocean_config):
            cluster_container = self.add_subgraph(cluster_obj, None)
            cluster_container.add_container(node_objects, config)

        # 2.4 Add all edges/connections
        self.add_connections(edge_objects, start_objects, end_objects,  [obj.upstream_role.name for obj in edge_objects])

        # 3.0 Generate graph coordinates
        self.generate_graph_coordinates()
