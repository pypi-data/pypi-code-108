""" Config parser for Cerberus """

import logging
import json
import hashlib

from cerberus.exceptions import *
from collections import defaultdict

class Validator():

    def __init__(self) -> None:
        pass
    
    def check_config(self, config, logname):
        """ Checks if the config file is valid """
        logger = self.get_logger(logname)
        err_msg = "Malformed config detected!\n"
        try:
            if "hosts_matrix" not in config:
                raise ConfigError(f"{err_msg}No 'hosts_matrix' found\n")
            if "switch_matrix" not in config:
                raise ConfigError(f"{err_msg}No 'hosts_matrix' found\n")
            self.check_hosts_config(config["hosts_matrix"])
            self.check_switch_config(config["switch_matrix"])
        except (ConfigError, ValueError) as err:
            logger.error(err)
            return False
        return True

    def check_hosts_config(self, host_matrix):
        """ Parses and validates the hosts matrix """
        err_msg = ("Malformed config detected in the hosts section!\n" +
                    "Please check the config:\n")
        if not host_matrix:
            raise ConfigError(f"{err_msg} hosts matrix is empty")
        for host in host_matrix:
            if "name" not in host:
                raise ConfigError(f"{err_msg} Host doesn't have a name")
            if "interfaces" not in host:
                raise ConfigError(f"{err_msg} Host has no interfaces")
            self.check_host_interfaces(err_msg, host)
        

    def check_host_interfaces(self, err_msg, host):
        """ Parse and validates the host's interfaces """
        err_msg = err_msg + f"Host: {host['name']} has an error"
        if not host["interfaces"]:
            raise ConfigError(f"{err_msg} interfaces section is empty")
        for iface in host["interfaces"]:
            if "swport" not in iface:
                raise ConfigError(f"{err_msg}. It has no switch port\n")
            self.check_valid_port(iface['swport'], err_msg)
            if "switch" not in iface:
                raise ConfigError(f"{err_msg}. It does not have an " +
                                    "assigned switch\n")
            if "ipv4" in iface:
                self.check_ipv4_address(err_msg, iface["ipv4"])
            if "ipv6" in iface:
                self.check_ipv6_address(err_msg, iface["ipv6"])
            if "ipv4" not in iface and "ipv6" not in iface:
                raise ConfigError(f"{err_msg}. It has neither an IPv4" +
                                    " or IPv6 address\n")
            if "mac" not in iface:
                iface["mac"] = self.check_for_available_mac(err_msg, iface, 
                                                            host["interfaces"])
            self.check_mac_address(err_msg, iface["mac"])
            if "vlan" in iface:
                self.check_vlan_validity(err_msg, iface["vlan"])


    def check_ipv4_address(self, err_msg, v4_address):
        """ Checks validity of ipv4 address """
        if not v4_address:
            raise ConfigError(f"{err_msg} please check that ipv4 sections" +
                                "have addresses assigned")
        if "." not in v4_address or "/" not in v4_address:
            raise ConfigError(f"{err_msg} in the ipv4 section. " +
                              f"IPv4 address: {v4_address}")

    def check_ipv6_address(self, err_msg, v6_address):
        """ Checks validity of ipv6 address """
        if not v6_address:
            raise ConfigError(f"{err_msg} please check that ipv6 sections" +
                                "have addresses assigned")
        if ":" not in v6_address or "/" not in v6_address:
            raise ConfigError(f"{err_msg} in the ipv6 section. " +
                                f"IPv6 address: {v6_address}")

    def check_mac_address(self, err_msg, mac_address):
        """ Checks validity of MAC address """
        if not mac_address:
            raise ConfigError(f"{err_msg} please check that MAC sections " +
                                "have addresses assigned")
        if ":" not in mac_address:
            raise ConfigError(f"{err_msg} in the MAC section. Currently " +
                                "only : seperated addresses are supported\n" +
                                f"MAC Address: {mac_address}\n")
        return True

    def check_for_available_mac(self, err_msg, iface, host_interfaces):
        """ Checks port if another mac address is assigned to the port """
        mac = ""
        for other_iface in host_interfaces:
            if iface is other_iface:
                continue

            if iface["switch"] == other_iface["switch"] and \
                    iface["swport"] == other_iface["swport"] and \
                    "mac" in other_iface:

                mac = other_iface["mac"]

        if not mac:
            raise ConfigError(f"{err_msg} in the mac section. " +
                                "No mac address was provided")
        return mac

    def check_vlan_validity(self, err_msg, vlan):
        """ Checks that the assigned vlan is a valid value """
        vid = int(vlan)
        if vid < 0 or vid > 4095:
            raise ConfigError(f"{err_msg}. Invalid vlan id(vid) detected. " +
                                "Vid should be between 1 and 4095. " +
                                f"Vid: {vid} detected\n")


    def check_switch_config(self, sw_matrix):
        """ Parses and validates the switch matrix """
        err_msg = ("Malformed config detected in the switch section!\n" +
                    "Please check the config:\n")
        if not sw_matrix:
            raise ConfigError(f"{err_msg}Switch matrix is empty")
        if "links" not in sw_matrix:
            raise ConfigError(f"{err_msg}No links section found")
        for link in sw_matrix["links"]:
            self.check_valid_link(link, err_msg)
        self.check_dp_ids(sw_matrix, err_msg)


    def check_dp_ids(self, sw_matrix, err_msg):
        """ Checks if the dp id section is valid in the  """
        if "dp_ids" not in sw_matrix:
            raise ConfigError(f"{err_msg}No dp_id section found!\n" +
                            "Please specify dp_ids to communicate with")
        else:
            for _, dp_id in sw_matrix["dp_ids"].items():
                if not int(dp_id):
                    raise ConfigError(f"{err_msg}Please ensure that dp_ids are"+ 
                                      f" valid numbers.\n dp_id found: {dp_id}")


    def check_valid_link(self, link, err_msg):
        """ Parses link and checks if it is valid """
        if len(link) != 4:
            raise ConfigError(f"{err_msg}Invalid link found. " +
                                "Expected link format:\n" +
                                "[switch1,switch1_port,switch2,switch2_port]\n" +
                                f"Link found: {link}")
        port_a = int(link[1])
        port_b = int(link[3])
        self.check_valid_port(port_a, err_msg)
        self.check_valid_port(port_b, err_msg)

    def check_valid_port(self, port, err_msg):
        """ Helper to check if ports are valid """
        self.check_port_number(port, err_msg)
        self.check_valid_port_range(port, err_msg)
    
    
    def check_valid_port_range(self, port, err_msg):
        """ Checks if the port is a valid number for Umbrella """
        if port < 0 or port > 255:
            raise ConfigError(f"{err_msg} Invalid port number detected. Ensure"+ 
                              " that port numbers are between 0 and 255\n"
                              f"Found port: {port}")

    def check_port_number(self, port, err_msg):
        """ Checks if the port is a number """
        if type(port) != int or type(port) != int:
            int(port)            
            if type(port) != int:
                ValueError(f"{err_msg} Port must be a number.\n" + 
                           f"Found port{port}")


    def get_logger(self, logname):
        """ Retrieve logger """
        return logging.getLogger(logname)

class Parser():

    def __init__(self, logname='parser'):
        self.logger = self.get_logger(logname)

    
    def parse_config(self, config):
        """ Helper to get all information needed to  """
        links = self.get_links(config)
        p4_switches = self.get_p4_switches(config)
        switches = self.setup_base_switch_dictionary(config)
        group_links = self.setup_group_links(links, switches)
        switches = self.link_hosts_to_switches(config, switches)

        return [links, p4_switches, switches, group_links]


    def get_dpids(self, config):
        """ Get and returns the dpids """
        return config['switch_matrix']['dp_ids']

    def get_links(self, config):
        """ Gets and returns the links """
        return list(config['switch_matrix']['links'])

    def get_p4_switches(self, config):
        """ Gets and returns list of p4 switches """
        if "p4" in config['switch_matrix']:
            return config['switch_matrix']['p4']
        return None
    
    def setup_base_switch_dictionary(self, config):
        """ Sets up the base dictionary per switch """
        switches = {}
        for (sw, dp_id) in config['switch_matrix']['dp_ids'].items():
            switches[sw] = {}
            switches[sw]['dp_id'] = self.format_dpid(dp_id)
            switches[sw]['name'] = sw
            switches[sw]['hosts'] = {}
        
        return switches

    
    def setup_group_links(self, links, switches):
        """ Setup the group links """
        group_links = {}
        for sw in switches:
            group_links[sw] = {}

        group_links = self.setup_directly_connectecd_group_links(links, 
                                                        switches, group_links)

        group_links = self.setup_indirect_group_links(links, switches, 
                                                      group_links)

        return group_links

    def setup_indirect_group_links(self, links, switches, group_links):
        
        isolated_switches = [s for s in group_links if len(group_links[s].values()) < 2]

        for sw in switches:
            if sw in isolated_switches:
                val = list(group_links[sw].values())[0]
                for other_sw, values in switches.items():
                    if other_sw == sw:
                        continue
                    group_links[sw][values['dp_id']] = val['main']
            else:
                for other_sw, details in switches.items():
                    if sw == other_sw:
                        continue
                    target_dp_id = details['dp_id']
                    if target_dp_id in group_links[sw]:
                        sw_link = group_links[sw][target_dp_id]
                        sw_link = self.find_link_backup_group(sw, sw_link,
                                                                links, group_links)
                        group_links[sw][target_dp_id] = sw_link

                    else:
                        route = self.find_route(links, sw, other_sw)

                        if route:
                            sw_link = self.find_indirect_group(sw, route,
                                        links, group_links, target_dp_id, switches)
                            group_links[sw][target_dp_id] = sw_link
        
        return group_links

    def find_link_backup_group(self, sw, link, links, group_links):
        """ Help to fill out group details for switches directly connected """
        other_sw = link['other_sw']
        l = [sw, link['main'], other_sw, link['other_port']]
        new_links = list(links)
        new_links = self.remove_old_link_for_ff(l, new_links)

        link = self.find_group_rule(new_links, sw, link, other_sw, group_links)

        return link


    def find_indirect_group(self, sw, route, links, group_links,
                            group_id, switches):
        """ Help to fill out group details for switches indirectly connected """

        next_hop_id = switches[route[1]]['dp_id']
        out_port = group_links[sw][next_hop_id]['main']
        group_links[sw][group_id] = {
                    "main": out_port,
                    "other_sw": route[1],
                    "other_port": group_links[sw][next_hop_id]['other_port']
                    }
        link = group_links[sw][group_id]

        link = self.find_link_backup_group(sw, link, links, group_links)

        return link


    def remove_old_link_for_ff(self, link_to_remove, links):
        """ Removes a local link to generate a topology with that link down and
            determine which paths to take for redundancy """
        new_links = list(links)
        if link_to_remove in new_links:
            new_links.remove(link_to_remove)
        else:
            li = [link_to_remove[2], link_to_remove[3],
                link_to_remove[0], link_to_remove[1]]
            try:
                new_links.remove(li)
            except:
                self.logger.error("Error trying to remove link from the core.")
                self.logger.error(f"Link to remove: {str(link_to_remove)}")
                self.logger.error(f"Link Array: {str(links)}")
        return new_links


    def find_group_rule(self, links, sw, sw_link, target_sw, group_links):
        """ Find the path between 2 switches and create links for them """
        route = self.find_route(links, sw, target_sw)
        if route:
            backup = [v['main'] for k,v in group_links[sw].items()
                      if route[1] == v['other_sw']]
            sw_link['backup'] = str(backup[0])

        return sw_link


    def setup_directly_connectecd_group_links(self, links: list, switches: list,
                                              group_links: dict):
        """Sets up the group link rules for switches that are directly connected

        Args:
            links (list): Array of core links
            switches (list): Array of switches
            group_links (dict): Dictionary that contains the details on which 
                                port the dp should use to reach another dp, 
                                based on their group_id

        Returns:
            [type]: [description]
        """
        for link in links:
            s1_id = switches[link[0]]['dp_id']
            s2_id = switches[link[2]]['dp_id']

            group_links = self.set_group_link(group_links, link[0], link[1], 
                                              link[2], s2_id, link[3])
            group_links = self.set_group_link(group_links, link[2], link[3],
                                              link[0], s1_id, link[1])

        return group_links


    def set_group_link(self, group_links, swname, own_port, dst_sw, dst_dp_id, dst_port):
        """ Helper to set main and backup paths for group link """
        group_links[swname][dst_dp_id] = {'main': own_port}
        group_links[swname][dst_dp_id]['other_sw'] = dst_sw
        group_links[swname][dst_dp_id]['other_port'] = dst_port
        return group_links

    def find_isolated_switches(self, group_links):
        """ Helper to find switches with only one core connection """
        isolated_switches = [s for s in group_links if len(group_links[s].values()) < 2]
        return isolated_switches
    
    def link_hosts_to_switches(self, config, switches):
        """ Configures the switches dictionary with hosts connected to it """
        for host in config['hosts_matrix']:
            host_name = host["name"]
            for iface in host["interfaces"]:
                if iface['switch'] not in switches:
                    self.logger.warning(f"Host: {host_name} is configured for "+
                                        f"the switch: {iface['switch']} which does not. " +
                                        "It will be ignored")
                    continue
                switches[iface['switch']]['hosts'].setdefault(iface['swport'], [])
                member = {}
                member['name'] = host_name
                member = self.find_and_add_mac(iface, member)
                member = self.find_and_add_v4(iface, member)
                member = self.find_and_add_v6(iface, member)
                member = self.find_and_add_vlan(iface, member)
                switches[iface['switch']]['hosts'][iface['swport']].append(member)
        return switches
                                

    def find_and_add_mac(self, iface, member):
        """ Finds if mac in iface and adds it to the dictionary """
        if 'mac' in iface:
            member['mac'] = iface['mac']             
        return member

    def find_and_add_v4(self, iface, member):
        """ Finds if ipv4 in iface and adds it to the dictionary """
        if 'ipv4' in iface:
            member['ipv4'] = iface['ipv4']             
        return member

    def find_and_add_v6(self, iface, member):
        """ Finds if ipv6 in iface and adds it to the dictionary """
        if 'ipv6' in iface:
            member['ipv6'] = iface['ipv6']             
        return member


    def find_and_add_vlan(self, iface, member):
        """ Finds if vlan in iface and adds it to the dictionary """
        if 'vlan' in iface:
            member['vlan'] = iface['vlan']
            member['tagged'] = iface['tagged']
        return member


    def get_hash(self, config):
        """ Stores the config as a hash, for quick comparisons """
        config_serialized = json.dumps(config)
        hashed_config = hashlib.sha256(config_serialized.encode())
        return hashed_config.hexdigest()


    def format_dpid(self, dp_id):
        """ Formats dp id to int for consistency """
        return int(dp_id)

    def get_logger(self, logname):
        """ Retrieve logger """
        return logging.getLogger(logname)


    def find_route(self, links, source_sw, target_sw):
        """ Helper method to return a route between two switches """
        link_nodes = self.spf_organise(links)
        spfgraph = Graph()
        for node in link_nodes:
            spfgraph.add_edge(*node)
        route = self.dijkstra(spfgraph, source_sw, target_sw)
        return route


    def spf_organise(self, links):
        """ Organises the links so that can be used for the shortest path """
        link_nodes = []
        for link in links:
            cost = 1000
            link_nodes.append([link[0], link[2], cost])
        return link_nodes


    def dijkstra(self, graph, initial, end):
        """ Dijkstra's algorithm used to determine shortest path """
        # shortest paths is a dict of nodes
        # whose value is a tuple of (previous node, weight)
        shortest_paths = {initial: (None, 0)}
        current_node = initial
        visited = set()

        while current_node != end:
            visited.add(current_node)
            destinations = graph.edges[current_node]
            weight_to_current_node = shortest_paths[current_node][1]

            for next_node in destinations:
                weight = graph.weights[(
                    current_node, next_node)] + weight_to_current_node
                if next_node not in shortest_paths:
                    shortest_paths[next_node] = (current_node, weight)
                else:
                    current_shortest_weight = shortest_paths[next_node][1]
                    if current_shortest_weight > weight:
                        shortest_paths[next_node] = (current_node, weight)

            next_destinations = {
                node: shortest_paths[node] for node in shortest_paths
                if node not in visited}
            if not next_destinations:
                return None
            # next node is the destination with the lowest weight
            current_node = min(next_destinations,
                               key=lambda k: next_destinations[k][1])

        # Work back through destinations in shortest path
        path = []
        while current_node is not None:
            path.append(current_node)
            next_node = shortest_paths[current_node][0]
            current_node = next_node
        # Reverse path
        path = path[::-1]
        return path


class Graph():
    """ Graphs all possible next nodes from a node """
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.weights = {}


    def add_edge(self, from_node, to_node, weight):
        """ Adds a new edge to existing node """
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight