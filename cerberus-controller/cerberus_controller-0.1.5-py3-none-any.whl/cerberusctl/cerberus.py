""" Proactive layer 2 Openflow Controller """

from collections import defaultdict
import logging
import json
from numbers import Integral
import os
import shutil
import sys
from typing import OrderedDict

from cerberus.config_parser import Validator, Parser
from cerberus.exceptions import *
from cerberus.api import api
from datetime import datetime
from pbr.version import VersionInfo
from ryu.app.wsgi import WSGIApplication
from ryu.base import app_manager
from ryu.controller import ofp_event, dpset, controller
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.lib.packet import ether_types

# Flow Tables
IN_TABLE = 0
OUT_TABLE = 1

DEFAULT_PRIORITY = 1500

DEFAULT_CONFIG = "/etc/cerberus/topology.json"
DEFAULT_LOG_PATH = "/var/log/cerberus"
DEFAULT_LOG_FILE = "/var/log/cerberus/cerberus.log"
DEFAULT_ROLLBACK_DIR = "/etc/cerberus/rollback"
DEFAULT_FAILED_CONF_DIR = "/etc/cerberus/failed"
DEFAULT_COOKIE = 525033

FLOW_NOT_FOUND = 0
FLOW_EXISTS = 1
FLOW_TO_UPDATE = 2
FLOW_OLD_DELETE = 3

class cerberus(app_manager.RyuApp):
    """ A RyuApp for proactively configuring layer 2 switches

    Cerberus removes MAC learning from the switching fabric for networks where
    the topologies are known in advanced
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'dpset': dpset.DPSet, 'wsgi': WSGIApplication}

    def __init__(self, cookie=DEFAULT_COOKIE, config_file_path=DEFAULT_CONFIG,
                 log_path=DEFAULT_LOG_FILE, rollback_dir=DEFAULT_ROLLBACK_DIR,
                 failed_directory=DEFAULT_FAILED_CONF_DIR, *_args, **_kwargs):
        super(cerberus, self).__init__(*_args, **_kwargs)
        self.wsgi = _kwargs['wsgi']
        self.wsgi.register(api, {'cerberus_main': self})
        self.dpset = _kwargs['dpset']
        self.logname = 'cerberus'
        self.rollback_dir = rollback_dir
        self.config_file_path = config_file_path
        self.failed_directory = failed_directory
        self.log_path = log_path
        self.logger = self.setup_logger(logfile = self.log_path)
        self.logger.info(f"Starting Cerberus {VersionInfo('cerberus')}")
        self.hashed_config = None
        self.config_file = None
        self.config = self.get_config_file()
        self.cookie = cookie

    def get_config_file(self, config_file: str = DEFAULT_CONFIG,
                        rollback_directory: str = DEFAULT_ROLLBACK_DIR,
                        failed_directory: str = DEFAULT_FAILED_CONF_DIR):
        """ Initial setup where configuration file is loaded

        Args:
            config_file (str, optional): Location where the configuration
                                         file is stored.
                                         Defaults to DEFAULT_CONFIG.
            rollback_directory (str, optional): Location where the rollback
                                                files are stored.
                                                Defaults to DEFAULT_ROLLBACK_DIR.
            failed_directory (str, optional): Loaction where the
                                              failed configurations are stored.
                                              Defaults to DEFAULT_FAILED_CONF_DIR.

        Returns:
            [type]: [description]
        """
        # TODO: Get config file from env if set
        conf_parser = Parser(self.logname)
        config = self.open_config_file(config_file)
        self.logger.info("Checking config file")
        if not Validator().check_config(config, self.logname):
            self.copy_failed_config_to_failed_dir(config_file, failed_directory)
            self.logger.error(f"Restart cerberus with a valid config. A copy " +
                              f"of the failed config has been stored in " +
                              f"{failed_directory}")
            if self.rollback_files_exist(rollback_directory):
                self.logger.error(f"Potential rollback files have been found " +
                                  f"in {rollback_directory}")
            sys.exit()

        prev_config = self.get_rollback_running_config(rollback_directory)
        if prev_config:
            self.logger.info(f"Previous config has been found")
            if not self.config_hashes_matches(config, prev_config):
                self.logger.info(f"Changes found, storing old config as backup")
                self.store_rollbacks(config_file, rollback_directory)
        else:
            self.store_rollbacks(config_file, rollback_directory)
        parsed_config = self.set_up_config_to_be_active(config)
        return parsed_config

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def datapath_connection_handler(self, ev: dpset.EventDP):
        """ Handler for when a datapath is connected

        Args:
            ev (dpset.EventDP): Event notifier that a datapath has connected
        """
        dp_id = self.format_dpid(ev.dp.id)
        if ev.enter:
            self.logger.info(f'Datapath: {dp_id} found')

            if self.datapath_to_be_configured(dp_id):
                self.logger.info(f"Datapath: {dp_id} to be configured")
                self.send_flow_stats_request(ev.dp)
                self.send_group_desc_stats_request(ev.dp)


    def sw_already_configured(self, datapath: controller.Datapath, flows: list):
        """ Checks whether a datapath is already configured.

        Args:
            datapath (controller.Datapath): The datapath that is
                                            being configured.
            flows (list): A list of all the OpenFlow flows that is expected to
                          be on the switch
        """
        dp_id = datapath.id
        sw_name = self.config['dp_id_to_sw_name'][dp_id]

        for switch in self.config['switches']:
            group_id = None
            if switch != sw_name:
                group_id = self.config['switches'][switch]['dp_id']
            for port, hosts in self.config['switches'][switch]['hosts'].items():
                for host in hosts:
                    flows = self.check_if_host_in_flows(datapath, host,
                                                        port, flows, group_id)


    def send_group_desc_stats_request(self, datapath: controller.Datapath):
        """ Send a request to retrieve the group description statistics.

        Args:
            datapath (controller.Datapath): Datapath to send the request to.
        """
        ofp_parser: ofproto_v1_3_parser
        ofp_parser = datapath.ofproto_parser
        ofp: ofproto_v1_3
        ofp = datapath.ofproto

        req = ofp_parser.OFPGroupDescStatsRequest(datapath, 0)

        datapath.send_msg(req)


    def send_flow_stats_request(self, datapath: controller.Datapath):
        """ Send a request to retrieve the flow description statistics.

        Args:
            datapath (controller.Datapath): Datapath to send the request to.
        """
        ofp_parser: ofproto_v1_3_parser
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER) #type: ignore
    def flow_stats_reply_handler(self, ev):
        """ Handler for the reply of OpenFlow statistics.

        Args:
            ev (EventOFPFlowStatsReply): OpenFlow flow statistics reply.
        """
        flows = []
        dp: controller.Datapath
        dp = ev.msg.datapath
        dp_id = dp.id
        stat: ofproto_v1_3_parser.OFPFlowStats
        for stat in ev.msg.body:
            flow = {"table_id": stat.table_id, "match": stat.match,
                    "instructions": stat.instructions, "cookie": stat.cookie}
            flows.append(flow)
        self.logger.debug(f"Datapath: {dp_id}\t FlowStats: {flows}")
        if len([f for f in flows if f['cookie'] == self.cookie]) < 1:
            self.logger.info(f"Datapath: {dp_id} will be configured")
            self.clear_flows(dp)
            self.full_sw_setup(dp)
        else:
            self.sw_already_configured(dp, flows)


    @set_ev_cls(ofp_event.EventOFPGroupDescStatsReply, MAIN_DISPATCHER) #type: ignore
    def group_desc_stat_reply_handler(self, ev):
        """ Handler for the reply of group description statistics request.

        Args:
            ev (EventOFPGroupDescStatsReply): OpenFlow group description
                                              statistics reply.
        """
        groups = []
        dp: controller.Datapath
        dp = ev.msg.datapath
        dp_id = dp.id
        stat: ofproto_v1_3_parser.OFPGroupDescStats
        for stat in ev.msg.body:
            groups.append({"group_id": stat.group_id, "buckets": stat.buckets})
        self.logger.info(f"Datapath: {dp_id} Groups: {groups}")

        if len(groups) < 1:
            self.setup_groups(dp)
        else:
            self.compare_and_update_groups(dp, groups)


    def full_sw_setup(self, datapath: controller.Datapath):
        """ Helper function to completely setup a datapath.

        Args:
            datapath (controller.Datapath): The datapath to setup.
        """
        dp_id = datapath.id
        # Assume that a switch with no flows have no groups
        # Groups needed for making group rules
        self.setup_groups(datapath)
        self.setup_sw_hosts(datapath)
        self.logger.info(f"Datapath: {dp_id} configured")

    def setup_sw_hosts(self, datapath: controller.Datapath):
        """ Configures a datapath with all the flows requried for
            host connectivity.

        Args:
            datapath (controller.Datapath): Datapath to be configured.
        """
        dp_id = datapath.id
        for switch in self.config['switches']:
            if self.format_dpid(dp_id) != self.config['switches'][switch]['dp_id']:
                group_id = self.config['switches'][switch]['dp_id']
                self.setup_flows_for_not_direct_connections(datapath,
                                                            switch,
                                                            int(group_id))
                continue
            for port, hosts in self.config['switches'][switch]['hosts'].items():
                for host in hosts:
                    host_name = host['name']
                    mac = host['mac']
                    vlan_id = host['vlan'] if 'vlan' in host else 0
                    tagged = host['tagged'] if 'tagged' in host else False
                    ipv4 = host['ipv4'] if 'ipv4' in host else ""
                    ipv6 = host['ipv6'] if 'ipv6' in host else ""
                    self.logger.info(f"Datapath: {dp_id}\tConfiguring host: "
                                     f"{host_name} on port: {port}")
                    self.logger.debug(f"Datapath: {dp_id}\t host: {host_name} "
                                      f"has mac: {mac}\tvlan: {vlan_id}\t"
                                      f"tagged: {tagged}\tipv4: {ipv4}\t"
                                      f"ipv6: {ipv6}")
                    self.add_in_flow(port, datapath, mac, vlan_id, tagged)
                    self.setup_flows_for_direct_connect(datapath, int(port),
                                                        host_name, mac, vlan_id,
                                                        tagged, ipv4, ipv6)


    def setup_flows_for_direct_connect(self, datapath: controller.Datapath,
                                       port: int, host_name: str, mac: str,
                                       vlan_id: int, tagged: bool, ipv4: str,
                                       ipv6: str):
        """ Helper function to setup flows for hosts that are directly connected
            to the datapath.

        Args:
            datapath (controller.Datapath): Datapath to configure.
            port (int): Openflow port number that host is connected to.
            host_name (str): Host name
            mac (str): Mac address of the host.
            vlan_id (str): The vlan id to use for this host.
            tagged (bool): If connections from the host will be vlan tagged.
            ipv4 (str): IPv4 address of the host.
            ipv6 (str): IPv6 address of the host.
        """
        self.add_direct_mac_flow(datapath, host_name, mac, vlan_id,
                                 tagged, port)
        self.add_direct_ipv4_flow(datapath, host_name, mac, ipv4, vlan_id,
                                  tagged, port)
        self.add_direct_ipv6_flow(datapath, host_name, mac, ipv6, vlan_id,
                                  tagged, port)


    def setup_flows_for_not_direct_connections(self,
                                               datapath: controller.Datapath,
                                               switch: str, group_id: int):
        """ Setup the flows for connections that are not directly connected to
            the datapath.

        Args:
            datapath (controller.Datapath): Datapath to configure.
            switch (str): Name of the destination switch that the
                          datapath is connecting to.
            group_id (int): The group id/datapath id of the destination switch.
        """
        for _, hosts in self.config['switches'][switch]['hosts'].items():
                for host in hosts:
                    host_name = host['name']
                    mac = host['mac']
                    vlan_id = host['vlan'] if 'vlan' in host else None
                    ipv4 = host['ipv4'] if 'ipv4' in host else None
                    ipv6 = host['ipv6'] if 'ipv6' in host else None
                    self.add_indirect_mac_flow(datapath, host_name, mac,
                                               vlan_id, group_id)
                    self.add_indirect_ipv4_flow(datapath, host_name, mac, ipv4,
                                                vlan_id, group_id)
                    self.add_indirect_ipv6_flow(datapath, host_name, mac, ipv6,
                                                vlan_id, group_id)

    def setup_groups(self, datapath: controller.Datapath):
        """ Initial setup for all the groups of the datapath.

        Args:
            datapath (controller.Datapath): The datapath to configure.
        """
        group_links = self.config['group_links']
        dp_name = self.config['dp_id_to_sw_name'][datapath.id]

        self.setup_core_in_table(datapath, dp_name)
        for target_dp_id, link in group_links[dp_name].items():
            self.add_group(datapath, link, target_dp_id)


    def add_group(self, datapath: controller.Datapath,
                  link: dict, group_id: int):
        """ Helper fucntion to build and add groups to the datapath.

        Args:
            datapath (controller.Datapath): The datapath to configure.
            link (dict): Link dictionary that contains the main and backup
                         ports to use to send traffic to the destination datapath.
            group_id (int): Group id of the the destination datapath.
        """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        buckets = self.build_group_buckets(datapath, link)
        msg = ofproto_parser.OFPGroupMod(datapath, ofproto.OFPGC_ADD,
                                         ofproto.OFPGT_FF, int(group_id),
                                         buckets)
        datapath.send_msg(msg)


    def update_group(self, datapath: controller.Datapath, buckets: dict,
                     group_id: int) -> None:
        """ Helper function to update groups in the datapath.

        Args:
            datapath (controller.Datapath): Datapath to update.
            buckets (dict): New bucket config to use.
            group_id (int): Group id that will be updated.
        """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        msg = ofproto_parser.OFPGroupMod(datapath, ofproto.OFPGC_MODIFY,
                                         ofproto.OFPGT_FF, int(group_id),
                                         buckets)
        datapath.send_msg(msg)


    def remove_group(self, datapath: controller.Datapath, group_id: int):
        """ Helper function to remove groups from the datapath

        Args:
            datapath (controller.Datapath): Datapath to remove groups from.
            group_id (int): The id of the group to remove.
        """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        msg = ofproto_parser.OFPGroupMod(datapath,
                                         command=ofproto.OFPGC_DELETE,
                                         group_id=group_id)
        datapath.send_msg(msg)


    def build_group_buckets(self, datapath: controller.Datapath, link: dict)-> \
                            "list[ofproto_v1_3_parser.OFPBucket]":
        """ Build the failover buckets for a link.

        Args:
            datapath (controller.Datapath): Datapath to build buckets for.
            link (dict): Group link dictionary.

        Returns:
            list[ofproto_v1_3_parser.OFPBucket]: List of failover buckets.
        """
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        main_port = int(link['main'])
        main_actions = [ofproto_parser.OFPActionOutput(main_port)]
        buckets = [ofproto_parser.OFPBucket(watch_port=main_port,
                                            actions=main_actions)]
        if 'backup' in link:
            backup_port = int(link['backup'])
            backup_actions = [ofproto_parser.OFPActionOutput(backup_port)]
            buckets.append(ofproto_parser.OFPBucket(watch_port=backup_port,
                                            actions=backup_actions))
        return buckets


    def add_direct_mac_flow(self, datapath: controller.Datapath, host_name: str,
                            mac: str, vid: int, tagged: bool, port: int,
                            priority: int=DEFAULT_PRIORITY,
                            cookie: int=DEFAULT_COOKIE):
        """ Helper function for adding a flow for a mac address of a host that
            is directly connected to the datapath.

        Args:
            datapath (controller.Datapath): Datapath to add the flow to.
            host_name (str): Host name of the destination host.
            mac (str): Host's mac address.
            vid (str): VLAN ID of the destination host.
            tagged (bool): If the flow should be tagged with a VLAN.
            port (int): Port the host is connected to.
            priority (int, optional): The priority of the flow. \
                                      Defaults to DEFAULT_PRIORITY.
            cookie (int, optional): The cookie to use when adding the flow. \
                                    Defaults to DEFAULT_COOKIE.
        """
        match, instructions = self.build_direct_mac_flow_out(datapath, mac, vid,
                                                             tagged, port)
        self.add_flow(datapath, match, instructions, OUT_TABLE, cookie, priority)


    def build_direct_mac_flow_out(self, datapath: controller.Datapath, mac: str,
            vid: int, tagged: bool, port: int):
        """ Builds match and instructions on the out table for a host's mac
            address that is directly connected to the datapath.

        Args:
            datapath (controller.Datapath): Datapath to add the flow to.
            mac (str): Host's mac address.
            vid (int): Peering vlan ID of the destination host.
            tagged (bool): If the flow needs to be tagged.
            port (int): Port the host is connected to.
        Returns:
            match, instructions \
                (tuple[ofproto_v1_3_parser.OFPMatch, \
                 list[ofproto_v1_3_parser.OFPInstructionActions]]): \
                    Tuple of the match and instructions.
        """

        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        instructions = []

        actions = []
        match = ofproto_parser.OFPMatch(vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                                        eth_dst=mac)
        if not tagged:
            actions.append(ofproto_parser.OFPActionPopVlan())
        actions.append(ofproto_parser.OFPActionOutput(port))
        instructions = [ofproto_parser.OFPInstructionActions(
                            ofproto.OFPIT_APPLY_ACTIONS,
                            actions)]
        return match, instructions

    def build_direct_mac_flow_in(self, datapath: controller.Datapath, mac: str,
                                 vid: int, tagged: bool, port: int):
        """ Builds match and instructions on the in table for a host's mac
            address that is directly connected to the datapath.

        Args:
            datapath (controller.Datapath): The datapath to configure.
            mac (str): Host's mac address.
            vid (int): Peering vlan ID of the host.
            tagged (bool): If the hosts connection will be tagged.
            port (int): Port of the host.

        Returns:
            match, instructions \
                (tuple[ofproto_v1_3_parser.OFPMatch, \
                 list[ofproto_v1_3_parser.OFPInstructionActions]]): \
                    Tuple of the match and instructions.
        """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        instructions = []
        if tagged:
            match = ofproto_parser.OFPMatch(in_port=port,
                        vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                        eth_src=mac)
        else:
            match = ofproto_parser.OFPMatch(in_port=port, eth_src=mac)
            tag_vlan_actions = [
                ofproto_parser.OFPActionPushVlan(),
                ofproto_parser.OFPActionSetField(
                    vlan_vid=(ofproto.OFPVID_PRESENT | vid))]

            actions = ofproto_parser.OFPInstructionActions(
                                ofproto.OFPIT_APPLY_ACTIONS,
                                tag_vlan_actions)
            instructions.append(actions)
        instructions.append(ofproto_parser.OFPInstructionGotoTable(OUT_TABLE))

        return match, instructions


    def add_direct_ipv4_flow(self, datapath: controller.Datapath,
                             host_name: str, mac: str, ipv4: str, vid: int,
                             tagged: bool, port: int,
                             priority: int=DEFAULT_PRIORITY,
                             cookie: int=DEFAULT_COOKIE):
        """ Helper function for adding a arp flow rule for a IPv4 address of a
            host that is directly connected to the datapath.

        Args:
            datapath (controller.Datapath): Datapath to add the flow to.
            host_name (str): Host name of the destination host.
            mac (str): Host's mac address.
            ipv4 (str): Host's ipv4 address.
            vid (int): Peering vlan id to use.
            tagged (bool): If the flow should be tagged.
            port (int): Port the host is connected to.
            priority (int, optional): The priority of the flow. \
                                      Defaults to DEFAULT_PRIORITY.
            cookie (int, optional): The cookie to use when adding the flow. \
                                    Defaults to DEFAULT_COOKIE.
        """
        match, instructions = self.build_direct_ipv4_out(datapath, mac, ipv4,
                                                         vid, tagged, port)
        # Add ipv4 arp rule for directly connected host
        self.add_flow(datapath, match, instructions, OUT_TABLE, cookie, priority)


    def build_direct_ipv4_out(self, datapath: controller.Datapath, mac: str,
                              ipv4:str, vid: int, tagged: bool, port: int):
        """ Builds the match and instructions on the out table for a host with
            a ipv4 address that is directly connected to the datapath.

        Args:
            datapath (controller.Datapath): Datapath to add the flow to.
            mac (str): Host's mac address.
            ipv4 (str): Host's ipv4 address.
            vid (int): Peering vlan of the host.
            tagged (bool): If a flow needs to be tagged.
            port (int): The port that the host is connected to.

        Returns:
            match, instructions \
                (tuple[ofproto_v1_3_parser.OFPMatch, \
                 list[ofproto_v1_3_parser.OFPInstructionActions]]): \
                    Tuple of the match and instructions.
        """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        actions = []
        match = ofproto_parser.OFPMatch(vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                                        eth_type=ether_types.ETH_TYPE_ARP,
                                        arp_tpa=self.clean_ip_address(ipv4))
        if not tagged:
            actions.append(ofproto_parser.OFPActionPopVlan())
        actions.append(ofproto_parser.OFPActionSetField(eth_dst=mac))
        actions.append(ofproto_parser.OFPActionOutput(port))
        instructions = [ofproto_parser.OFPInstructionActions(
                            ofproto.OFPIT_APPLY_ACTIONS,
                            actions)]

        return match, instructions


    def add_direct_ipv6_flow(self, datapath, host_name, mac, ipv6, vid, tagged,
                             port, priority=DEFAULT_PRIORITY,
                             cookie=DEFAULT_COOKIE):
        """ Add ipv6 arp rule for directly connected host """
        match, instructions = self.build_direct_ipv6_out(datapath, mac, ipv6,
                                                         vid, tagged, port)
        self.add_flow(datapath, match, instructions, OUT_TABLE, cookie, priority)


    def build_direct_ipv6_out(self, datapath: controller.Datapath, mac, ipv6,
                              vid, tagged, port):
        """ Builds the match and instructions for IPv6 flows of hosts that are
            are directly connected """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        actions = []
        match = ofproto_parser.OFPMatch(vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                                    icmpv6_type=135, ip_proto=58,
                                    eth_type=34525,
                                    ipv6_nd_target=self.clean_ip_address(ipv6))
        if not tagged:
            actions.append(ofproto_parser.OFPActionPopVlan())
        actions.append(ofproto_parser.OFPActionSetField(eth_dst=mac))
        actions.append(ofproto_parser.OFPActionOutput(port))

        instructions = [ofproto_parser.OFPInstructionActions(
                            ofproto.OFPIT_APPLY_ACTIONS,
                            actions)]
        return match, instructions


    def add_indirect_mac_flow(self, datapath, host_name, mac, vid, group_id,
                              priority=DEFAULT_PRIORITY, cookie=DEFAULT_COOKIE):
        """ Add mac rule for indirectly connected hosts """
        match, instructions = self.build_indirect_mac_flow_out(datapath, mac,
                                                          vid, group_id)
        self.add_flow(datapath, match, instructions, OUT_TABLE, cookie, priority)


    def build_indirect_mac_flow_out(self, datapath: controller.Datapath, mac,
                                    vid, group_id):
        """ Builds the flow and instructions for mac flows of hosts
            inderectly connected """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        instructions = []

        match = ofproto_parser.OFPMatch(vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                                        eth_dst=mac)

        instructions = [ofproto_parser.OFPInstructionActions(
                            ofproto.OFPIT_APPLY_ACTIONS,
                            [ofproto_parser.OFPActionGroup(group_id)])]
        return match, instructions


    def add_indirect_ipv4_flow(self, datapath, host_name, mac, ipv4, vid,
                               group_id, priority=DEFAULT_PRIORITY,
                               cookie=DEFAULT_COOKIE):
        """ Add ipv4 rule for inderectly connected hosts """
        match, instructions = self.build_indirect_ipv4_out(datapath, mac, ipv4,
                                                           vid, group_id)
        self.add_flow(datapath, match, instructions, OUT_TABLE, cookie, priority)


    def build_indirect_ipv4_out(self, datapath: controller.Datapath, mac, ipv4,
                                vid, group_id):
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        instructions = []

        match = ofproto_parser.OFPMatch(vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                                        eth_type=ether_types.ETH_TYPE_ARP,
                                        arp_tpa=self.clean_ip_address(ipv4))

        instructions = [ofproto_parser.OFPInstructionActions(
                            ofproto.OFPIT_APPLY_ACTIONS,
                            [ofproto_parser.OFPActionSetField(eth_dst=mac),
                             ofproto_parser.OFPActionGroup(group_id)])]
        return match, instructions


    def add_indirect_ipv6_flow(self, datapath, host_name, mac, ipv6, vid,
                               group_id, priority=DEFAULT_PRIORITY,
                               cookie=DEFAULT_COOKIE):
        """ Add ipv6 rule for inderectly connected hosts """
        match, instructions = self.build_indirect_ipv6_out(datapath, mac, ipv6,
                                                           vid, group_id)
        self.add_flow(datapath, match, instructions, OUT_TABLE, cookie, priority)


    def build_indirect_ipv6_out(self, datapath: controller.Datapath, mac, ipv6,
                                vid, group_id):
        """ Builds the match and instructions for IPv6 flows of hosts that are
            are directly connected """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser
        match = None
        instructions = []

        match = ofproto_parser.OFPMatch(vlan_vid=(ofproto.OFPVID_PRESENT | vid),
                                        icmpv6_type=135, ip_proto=58,
                                        eth_type=34525,
                                        ipv6_nd_target=self.clean_ip_address(ipv6))

        instructions = [ofproto_parser.OFPInstructionActions(
                            ofproto.OFPIT_APPLY_ACTIONS,
                            [ofproto_parser.OFPActionSetField(eth_dst=mac),
                             ofproto_parser.OFPActionGroup(group_id)])]

        return match, instructions


    def add_in_flow(self, port, datapath, mac=None, vlan=None, tagged=False,
                    priority=DEFAULT_PRIORITY, cookie=DEFAULT_COOKIE):
        """ Constructs flow for in table """
        ofproto_parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        match = None
        actions = []
        if mac:
            match, actions = self.build_direct_mac_flow_in(datapath, mac, vlan,
                                                           tagged, port)
        else:
            match = ofproto_parser.OFPMatch(in_port=port)
            actions.append(ofproto_parser.OFPInstructionGotoTable(OUT_TABLE))
        self.add_flow(datapath, match, actions, IN_TABLE, cookie, priority)


    def add_flow(self, datapath, match, actions, table, cookie=DEFAULT_COOKIE,
                 priority=DEFAULT_PRIORITY):
        """ Helper to a flow to the switch """
        parser = datapath.ofproto_parser
        flow_mod = parser.OFPFlowMod(datapath=datapath, match=match,
                                     instructions=actions, table_id=table,
                                     priority=priority, cookie=cookie)
        datapath.send_msg(flow_mod)


    def remove_flow(self, datapath, match, instructions, table_id):
        """ Helper to remove a particular rule from the datapath """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser

        flow_mod = ofproto_parser.OFPFlowMod(datapath=datapath,
                                             command=ofproto.OFPFC_DELETE,
                                             table_id=table_id,
                                             match=match,
                                             instructions=instructions)
        datapath.send_msg(flow_mod)


    def update_flow(self, datapath, match, instructions, table_id):
        """ Helper to update a rule on the datapath """
        ofproto: ofproto_v1_3
        ofproto = datapath.ofproto
        ofproto_parser: ofproto_v1_3_parser
        ofproto_parser = datapath.ofproto_parser

        flow_mod = ofproto_parser.OFPFlowMod(datapath=datapath,
                                             command=ofproto.OFPFC_MODIFY,
                                             table_id=table_id,
                                             match=match,
                                             instructions=instructions)
        datapath.send_msg(flow_mod)


    def update_sw(self, datapath):
        """ Helper to get rules and update the rules on the switch """
        pass


    def setup_core_in_table(self, datapath, switch):
        """ Initial setup flows for in table """
        for _, link in self.config['group_links'][switch].items():
            port = int(link['main'])
            self.add_in_flow(datapath=datapath, port=port)


    def datapath_to_be_configured(self, dp_id):
        """ Checks if the datapath needs to be configured """
        for sw in self.config['switches']:
            if dp_id == self.config['switches'][sw]['dp_id']:
                return True

        self.logger.warning(f'Datapath: {dp_id}\t has not been configured.')
        return False


    def clear_flows(self, datapath):
        """ Resets the flows on the datapath """
        ofproto = datapath.ofproto
        ofproto_parser = datapath.ofproto_parser
        flow_mod = ofproto_parser.OFPFlowMod(datapath=datapath,
                                             command=ofproto.OFPFC_DELETE,
                                             table_id=ofproto.OFPTT_ALL,
                                             out_port=ofproto.OFPP_ANY,
                                             out_group=ofproto.OFPG_ANY
                                             )
        datapath.send_msg(flow_mod)


    def clean_ip_address(self, address):
        """ Cleans address if an address range is found """
        if "/" in address:
            clean_address = address.split('/')[0]
            return clean_address
        return address


    def open_config_file(self, config_file):
        """ Reads the config file """
        data = None
        try:
            with open(config_file) as json_file:
                data = json.load(json_file)
        except (UnicodeDecodeError, PermissionError) as err:
            self.logger.error(f"Error in config file: {config_file}\n{err}")
            sys.exit()
        except ValueError as err:
            if os.path.getsize(config_file) == 0:
                self.logger.error(f"Error in opening config file: {config_file}"
                                  f"\nEnsure that the config file is not empty")
            else:
                self.logger.error(f"There was a problem in the config file: "
                                  f"{config_file}\n{err}")
            sys.exit()
        except (FileNotFoundError) as err:
            self.logger.error(f"File not found: {config_file}\n")
            if config_file is DEFAULT_CONFIG:
                self.logger.error(
                    f"Please specify a topology in {DEFAULT_CONFIG} or " +
                    "specify a config using the --config option")
            sys.exit()

        return data


    def store_config(self, config, config_file_path: str):
        try:
            with open(config_file_path, 'w') as json_file:
                self.logger.debug('Writing new config to be used as main config')
                json.dump(config, json_file, indent=2)
        except FileNotFoundError:
            self.logger.error(f"The file at {config_file_path} does not exist")
        except Exception as err:
            self.logger.error(f"Error when storing the config to "
                              f"{config_file_path}:\n{err}")


    def copy_config_file_to_running(self, config_file, rollback_directory):

        now = datetime.now()
        datefmt = "%Y-%m-%dT%H:%M:%S"
        running_conf_fname = f"{now.strftime(datefmt)}.running"
        rollback_fname = f"{rollback_directory}/{running_conf_fname}"
        self.logger.info(f"Copying over {config_file} to {rollback_fname}")
        shutil.copy(config_file, rollback_fname)


    def store_rollbacks(self, config_file, rollback_directory: str):
        """ Stores the running config file in the rollback area, and move the
            previous running config to rollback """
        now = datetime.now()
        datefmt = "%Y-%m-%dT%H:%M:%S"
        running_conf_fname = f"{now.strftime(datefmt)}.running"
        rollback_fname = f"{rollback_directory}/{running_conf_fname}"
        try:
            file_list = os.listdir(rollback_directory)
            self.logger.debug(f'There are {len(file_list)} files in the rollback directory')
            if len(file_list) > 0:
                rollback_files = [f for f in file_list if f.endswith('.rollback')]
                running_files = [f for f in file_list if f.endswith('.running')]

                if len(rollback_files) > 0:
                    self.logger.debug(f"There are {len(rollback_files)} rollback files in the rollback directory")
                    for rollback_file in rollback_files:
                        self.move_rollback_conf_to_backups(
                            f"{rollback_directory}/{rollback_file}")
                if len(running_files) > 0:
                    self.logger.debug(f"There are {len(running_files)} running files in the rollback directory")
                    for running_file in running_files:
                        self.move_running_conf_to_rollback(
                            f"{rollback_directory}/{running_file}")
            self.copy_config_file_to_running(config_file, rollback_directory)
        except Exception as err:
            self.logger.error("Error storing rollback")
            self.logger.error(f"confname: {config_file}\n "
                              f"storing location: "
                              f"{rollback_directory}/{running_conf_fname}")
            self.logger.error(err)


    def move_rollback_conf_to_backups(self, rollback_file):
        """ Stores the last rollback config to the list of backup files """
        try:
            cleaned_roll_back_name = f"{rollback_file.split('.')[0]}.json"
            self.logger.info(f"Moving file {rollback_file} to"
                              f" {cleaned_roll_back_name}")
            shutil.move(rollback_file, cleaned_roll_back_name)
        except Exception as err:
            self.logger.error("Error in storing the backups")
            self.logger.error(f"Rollback filename:{rollback_file}")
            self.logger.error(err)


    def move_running_conf_to_rollback(self, running_file):
        """ Sores the last running config to be the rollback config """
        try:
            new_rollback_name = f"{running_file.split('.')[0]}.rollback"
            self.logger.info(f"Moving file {running_file} to"
                              f" {new_rollback_name}")
            shutil.move(running_file, new_rollback_name)
        except Exception as err:
            self.logger.error("Error in moving the running file to be rollback")
            self.logger.error(f"Running conf name:{running_file}")
            self.logger.error(err)


    def rollback_API_config(self, config, failed_config_directory):

        current_main_config_stored = self.open_config_file(self.config_file_path)
        self.write_failed_config_to_failed_dir(config, failed_config_directory)
        prev_config = self.get_rollback_running_config(self.rollback_dir)
        if self.config_hashes_matches(config, current_main_config_stored):
            if prev_config and self.config_hashes_matches(config, prev_config):
                prev_config = self.get_rollback_running_config(self.rollback_dir, False)
            self.logger.info("Reverting changes made to running config file")
            self.store_config(prev_config, self.config_file_path)
        if self.config_hashes_matches(config, self.config_file):
            self.logger.info("Restoring config used in cerberus to rollback config")
            self.config = self.set_up_config_to_be_active(prev_config)


    def write_failed_config_to_failed_dir(self, config: dict,
                                          failed_conf_directory: str):
        try:
            filename = f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.failed_config"
            filepath = f"{failed_conf_directory}/{filename}"
            with open(filepath, 'w+') as file:
                json.dump(config, file, indent=2)
        except Exception as err:
            self.logger.error("Error in writing failed API config to failed directory")
            pass


    def copy_failed_config_to_failed_dir(self, config_file: str,
                                         failed_conf_directory: str):
        """ Copy a failed config to the failed config directory for analysis
            later. This is primarily to help with scripting issues

        Args:
            config_file (str): Path of failed config file to store in the failed
                               directory
            failed_conf_directory (str): Directory where failed configs are
                                         to be stored
        """
        try:
            shutil.copy(config_file, f"{failed_conf_directory}/{config_file}")
        except Exception as err:
            self.logger.error("Error storing the failed config in the failed" +
                              f"config directory! (Ironic isn't it?)")
            self.logger.error(f"Failed to copy: {config_file} " +
                              f"into: {failed_conf_directory}")


    def rollback_files_exist(self, rollback_directory: str) -> bool:
        """ Goes through the rollback directory and see if there are any
            potential candidates to rollback to

        Args:
            rollback_directory (str): Directory to search rollback files in

        Returns:
            bool: rollback Candidate exists
        """
        if len(os.listdir(rollback_directory)) < 1:
            return False
        file_list = [f for f in os.listdir(rollback_directory)
                     if f.endswith(".running")
                     or f.endswith(".rollback")
                     or f.endswith(".json")]
        if len(file_list) > 0:
            return True
        return False


    def get_rollback_running_config(self, rollback_directory: str,
                                    rolling_back_to_last_running: bool = True):
        """Finds the previous running config to use for roll back

        Args:
            rollback_directory (str): Directory to look in for rollback config
            files

        Returns:
            dict: Config file or None if no file is found
        """
        try:
            if not self.rollback_files_exist(rollback_directory):
                return None
            file_list = [f for f in os.listdir(rollback_directory)
                         if f.endswith(".running")]
            # Look to see if there was a previous working running config
            if rolling_back_to_last_running and len(file_list) > 0:
                last_running_conf = file_list[0]
                return self.open_config_file(
                    f"{rollback_directory}/{last_running_conf}")
            # If not see if there is a previous rollback file
            if len([f for f in os.listdir(rollback_directory)
                    if f.endswith(".rollback")]) > 0:
                rollback_file = [f for f in os.listdir(rollback_directory)
                                 if f.endswith(".rollback")][0]
                return self.open_config_file(
                                    f"{rollback_directory}/{rollback_file}")
            # Looks even further back to see if there are any previous files at all
            # Here be dragons
            if len([f for f in os.listdir(rollback_directory)
                    if f.endswith(".json")]) > 0:
                files = [f for f in os.listdir(rollback_directory)
                         if f.endswith(".json")]
                sorted_files = sorted(files, reverse=True)
                conf_to_load = sorted_files[0]
                return self.open_config_file(
                            f"{rollback_directory}/{conf_to_load}")
            # Files found but does not meet any criteria for rollback
            return None
        except Exception as err:
            self.logger.error("Error in retrieving the last known " +
                              "running config")
            self.logger.error(err)


    def rollback_current_config(self, rollback_dir: str = DEFAULT_ROLLBACK_DIR,
                                rollback_file: str = None, from_api = False):

        if rollback_file is None:
            rollback_config = self.get_rollback_running_config(rollback_dir)
            if self.config_hashes_matches(self.config, rollback_config):
                rollback_config = self.get_rollback_running_config(rollback_dir,
                                                                   False)
            if rollback_config is None:
                return
        pass


    def get_file_to_rollback_to(self, rollback_directory,
                                rolling_back_to_last_running: bool=True,
                                rollback_to_file: str=None):
        try:
            filepath = ""
            if not self.rollback_files_exist(rollback_directory):
                return filepath
            file_list = self.lists_rollback_files(rollback_directory)
            if rollback_to_file:
                if rollback_to_file in file_list:
                    filepath = f"{rollback_directory}/{rollback_to_file}"
            elif rolling_back_to_last_running:
                file = [f for f in file_list if f.endswith(".running")][0]
                filepath = f"{rollback_directory}/{file}"
            else:
                files = [f for f in file_list if f.endswith(".rollback")][0]
                # Ensure we get the latest rollback file
                sorted_files = sorted(files, reverse=True)
                file = sorted_files[0]
                filepath = f"{rollback_directory}/{file}"
            return filepath
        except FileNotFoundError as err:
            self.logger.error(f"Error in trying to get the latest "
                              f"rollback file: {err}")


    def lists_rollback_files(self, rollback_directory: str) -> list:
        """Retrieves the list of rollback files within the rollback directory.

        Args:
            rollback_directory (str): Directory that contains all potential
                                      rollback files

        Returns:
            [str]: [List of potential rollback files]
        """
        file_list = os.listdir(rollback_directory)
        return file_list


    def compare_and_update_groups(self, datapath: controller.Datapath, groups):
        """ Compares pulled rules with generated rules to see if they need to
            be added,updated or removed """
        config_parser = Parser(self.logname)
        group_links = self.config['group_links']
        dp_name = self.config['dp_id_to_sw_name'][datapath.id]
        switches = self.config['switches']
        links = self.config['links']
        isolated_switches = Parser(self.logname).find_isolated_switches(group_links)

        if dp_name in isolated_switches:
            for group_id in isolated_switches[dp_name]:
                link = isolated_switches[dp_name][group_id]
                buckets = self.build_group_buckets(datapath, link)
                groups = self.assess_groups(datapath, groups, group_id,
                                            buckets, link)
        else:
            for other_sw, details in switches.items():
                if dp_name == other_sw:
                    continue
                target_dp_id = details['dp_id']
                if target_dp_id in group_links[dp_name]:
                    link = group_links[dp_name][target_dp_id]
                    if 'backup' not in link:
                        link = config_parser.find_link_backup_group(dp_name,
                                                    link, links, group_links)
                    buckets = self.build_group_buckets(datapath, link)
                    groups = self.assess_groups(datapath, groups, target_dp_id,
                                                buckets, link)
                else:
                    route = config_parser.find_route(links, dp_name, other_sw)

                    if route:
                        sw_link = config_parser.find_indirect_group(dp_name,
                                                route, links, group_links,
                                                target_dp_id, switches)
                        buckets = self.build_group_buckets(datapath, sw_link)
                        groups = self.assess_groups(datapath, groups,
                                    target_dp_id, buckets, sw_link)

        if len(groups) > 1:
            for group in groups:
                self.remove_group(datapath, group['group_id'])
        return


    def assess_groups(self, datapath, groups, group_id, buckets, link):
        """ Assess whether a group and bucket combination exists """
        if self.buckets_groups_match(groups, group_id, buckets):
            # Remove group if it's been found
            groups = [g for g in groups if g['group_id'] != group_id]
            return groups
        if self.group_id_exists(groups, group_id):
            # Remove group if it's been found
            groups = [g for g in groups if g['group_id'] != group_id]
            self.update_group(datapath, buckets, group_id)
            return groups
        self.add_group(datapath, link, group_id)
        return groups


    def group_id_exists(self, groups, group_id):
        """ Checks to see if the group_id is present on the switch """
        for group in groups:
            if group_id == group['group_id']:
                return True
        return False


    def buckets_groups_match(self, groups, group_id, buckets):
        """ Checks to ensure that the group on the switch matches the
            expected group """

        for group in groups:
            if group_id == group['group_id'] and buckets == group['buckets']:
                return True
        return False


    def check_if_host_in_flows(self, datapath: controller.Datapath, host, port,
                               flows, group_id=None):
        """ Helper function to see if a host exists on the switch """
        host_name = host['name']
        mac = host['mac']
        vlan_id = host['vlan'] if 'vlan' in host else 0
        tagged = host['tagged'] if 'tagged' in host else False
        ipv4 = host['ipv4'] if 'ipv4' in host else ""
        ipv6 = host['ipv6'] if 'ipv6' in host else ""

        mac_result, flows = self.check_mac_flow_exist(datapath,
                                        mac, vlan_id, tagged, port,
                                        flows, group_id)
        if mac_result == FLOW_NOT_FOUND or mac_result == FLOW_OLD_DELETE:
            if group_id:
                self.add_indirect_mac_flow(datapath, host_name, mac,
                                           vlan_id, group_id)
            else:
                self.add_direct_mac_flow(datapath, host_name, mac,
                                         vlan_id, tagged, port)
                self.add_in_flow(port, datapath, mac, vlan_id, tagged)

        if ipv4:
            v4_result, flows = self.check_ipv4_flow_exist(datapath,
                                                mac, ipv4, vlan_id, tagged,
                                                port, flows, group_id)
            if v4_result == FLOW_NOT_FOUND or v4_result == FLOW_OLD_DELETE:
                if group_id:
                    self.add_indirect_ipv4_flow(datapath, host_name, mac, ipv4,
                                                vlan_id, group_id)
                else:
                    self.add_direct_ipv4_flow(datapath, host_name, mac, ipv4,
                                              vlan_id, tagged, port)
            if v4_result == FLOW_TO_UPDATE:
                if group_id:
                    match, inst = self.build_indirect_ipv4_out(datapath, mac,
                                                        ipv4, vlan_id, group_id)
                else:
                    match, inst = self.build_direct_ipv4_out(datapath, mac,
                                                    ipv4, vlan_id, tagged, port)
                self.update_flow(datapath, match, inst, OUT_TABLE)
        if ipv6:
            v6_result, flows = self.check_ipv6_flow_exist(datapath, mac, ipv6,
                                        vlan_id, tagged, port, flows, group_id)
            if v6_result == FLOW_NOT_FOUND or v6_result == FLOW_OLD_DELETE:
                if group_id:
                    self.add_indirect_ipv6_flow(datapath, host_name, mac, ipv6,
                                                vlan_id, group_id)
                else:
                    self.add_direct_ipv6_flow(datapath, host_name, mac, ipv6,
                                              vlan_id, tagged, port)
            if v6_result == FLOW_TO_UPDATE:
                if group_id:
                    match, inst = self.build_indirect_ipv6_out(datapath, mac,
                                                        ipv6, vlan_id, group_id)
                else:
                    match, inst = self.build_direct_ipv6_out(datapath,
                                            host_name, mac, ipv6, vlan_id, port)
                    self.update_flow(datapath, match, inst, OUT_TABLE)

        return flows


    def check_ipv6_flow_exist(self, datapath, mac, ipv6, vlan_id, tagged,
                                  port, flows, group_id=None):
        """ Checks if the ipv6 address exists in the flow table """
        exists = FLOW_NOT_FOUND

        if not group_id:
            match, inst = self.build_direct_ipv6_out(datapath, mac, ipv6,
                                                     vlan_id, tagged, port)
        else:
            match, inst = self.build_indirect_ipv6_out(datapath, mac, ipv6,
                                                       vlan_id, group_id)

        out_flows = [f for f in flows if f['table_id'] == OUT_TABLE]
        exists, flow = self.check_if_flows_match(out_flows, match, inst)

        if exists != FLOW_NOT_FOUND:
            flows.remove(flow)

        if exists == FLOW_OLD_DELETE:
            self.remove_flow(datapath, flow['match'], flow['instructions'],
                             OUT_TABLE)

        return exists, flows


    def check_ipv4_flow_exist(self, datapath, mac, ipv4, vlan_id, tagged,
                                  port, flows, group_id=None):
        """ Checks if the ipv4 address exists in the flow table """
        exists = FLOW_NOT_FOUND

        if not group_id:
            match, inst = self.build_direct_ipv4_out(datapath, mac, ipv4,
                                                     vlan_id, tagged, port)
        else:
            match, inst = self.build_indirect_ipv4_out(datapath, mac, ipv4,
                                                       vlan_id, group_id)

        out_flows = [f for f in flows if f['table_id'] == OUT_TABLE]

        exists, flow = self.check_if_flows_match(out_flows, match, inst)

        if exists != FLOW_NOT_FOUND:
            flows.remove(flow)
        if exists == FLOW_OLD_DELETE:
            self.remove_flow(datapath, flow['match'], flow['instructions'],
                             OUT_TABLE)

        return exists, flows


    def check_mac_flow_exist(self, datapath, mac, vlan_id, tagged, port,
                                 flows, group_id=None):
        """ Checks to see if the mac address exists in the flow table """
        exists = FLOW_NOT_FOUND
        in_flows = [f for f in flows if ['table_id'] == IN_TABLE]
        out_flows = [f for f in flows if f['table_id'] == OUT_TABLE]
        if not group_id:
            in_match, in_inst = self.build_direct_mac_flow_in(datapath, mac,
                                                              vlan_id, tagged,
                                                              port)
            exists, flow = self.check_if_flows_match(in_flows, in_match, in_inst)
            if exists == FLOW_NOT_FOUND:
                return exists, flows

            flows.remove(flow)
            out_match, out_inst = self.build_direct_mac_flow_out(datapath, mac,
                                                        vlan_id, tagged, port)
            if exists == FLOW_OLD_DELETE:
                self.remove_flow(datapath, flow['match'], flow['instructions'],
                                 IN_TABLE)
                _, out_flow = self.check_if_flows_match(out_flows, out_match,
                                                        out_inst)
                flows.remove(out_flow)
                self.remove_flow(datapath, out_flow['match'],
                                 out_flow['instructions'], OUT_TABLE)
                return exists, flows

            if exists == FLOW_TO_UPDATE:
                self.update_flow(datapath, in_match, in_inst, IN_TABLE)
                _, out_flow = self.check_if_flows_match(out_flows, out_match,
                                                        out_inst)
                flows.remove(out_flow)
                self.update_flow(datapath, out_match, out_inst, OUT_TABLE)
                return exists, flows

        else:
            out_match, out_inst = self.build_indirect_mac_flow_out(datapath, mac,
                                                            vlan_id, group_id)

        exists, flow = self.check_if_flows_match(out_flows, out_match, out_inst)
        if exists != FLOW_NOT_FOUND:
            flows.remove(flow)
        if exists == FLOW_OLD_DELETE:
            self.remove_flow(datapath, flow['match'], flow['instructions'],
                             OUT_TABLE)
        return exists, flows


    def check_if_flows_match(self, flows, match, instructions):
        """ Helper to see if a generated flow matches a pulled one """
        exists = FLOW_NOT_FOUND
        for flow in flows:
            if match in flow['match'] and instructions in flow['instructions']:
                exists = FLOW_EXISTS
                return exists, flow
            # Only check match, since we can't update the match part
            if match in flow['match']:
                exists = FLOW_TO_UPDATE
                return exists, flow
            if instructions in flow['instructions']:
                exists = FLOW_OLD_DELETE
                return exists, flow
        return exists, {}


    def associate_dp_id_to_swname(self, switches):
        """ Sets up dictionary to simplify retreiving a switch name when only
            having a dpid """

        dp_id_to_swname = {}
        for switch in switches:
            dp_id = switches[switch]['dp_id']
            dp_id_to_swname[dp_id] = switch
        return dp_id_to_swname


    def format_dpid(self, dp_id):
        """ Formats dp id to int for consistency """
        return int(dp_id)



################################################################
# API CALLS SECTION
################################################################

    def hello_world(self):
        """ Hello World tester to test the API """
        json_string = {"resp": "hello_world"}
        return json_string

    def get_switches(self):
        # json_string = self.config['switches']
        return self.config['switches']

    def get_running_config(self):
        # json_string = json.dumps(self.config)
        return self.config

    def get_running_config_file(self):
         return self.config_file


    def push_new_config(self, raw_config):
        config  = json.loads(raw_config)
        msg = self.compare_new_config_with_stored_config(config)
        if len(msg['changes']) > 0:
            try:
                self.store_config(config, self.config_file_path)
                self.store_rollbacks(self.config_file_path, self.rollback_dir)
                self.config = self.set_up_config_to_be_active(config)
                for switch in self.config['switches']:
                    dpid = self.config['switches'][switch]['dp_id']
                    dp = self.dpset.get(dpid)
                    # Need to send flow stats request which will trigger a flow
                    # table update
                    self.send_flow_stats_request(dp)
                    self.send_group_desc_stats_request(dp)
            except Exception as err:
                self.logger.error(f"Failed to apply new config, rolling back to"
                                  "previous working config")
                self.logger.error(err)
                self.rollback_API_config(config, self.failed_directory)
                msg['status'] = "error"
                msg['msg'] = ("The new config could not be applied, no "
                              "changes were made to the running config."
                              f"Error msg: {err}")
                msg['changes'] = []

        return msg

################################################################
# API CALLS SECTION END
################################################################

    def config_hashes_matches(self, config: dict, old_config: dict=None) ->bool:
        """ Transforms config to a hash and compare it with the existing one

        Args:
            config (dict): New config to compare hash with
            old_config (dict): Optional old config to compare with
        Returns:
            bool: Whether config matches
        """
        conf_parser = Parser(self.logname)
        sorted_config =  OrderedDict(config.items())
        new_conf_hash = conf_parser.get_hash(sorted_config)
        hash_to_compare = None
        if old_config:
            hash_to_compare = conf_parser.get_hash(OrderedDict(old_config.items()))
        elif self.hashed_config:
            hash_to_compare = self.hashed_config
        elif self.config_file:
            hash_to_compare = conf_parser.get_hash(OrderedDict(self.config_file))

        if not hash_to_compare:
            return False
        if new_conf_hash == hash_to_compare:
            return True
        return False


    def compare_new_config_with_stored_config(self, config):
        """Compare the new config with the one that is currently being used

        Args:
            config (dict): New config to compare with the existing config
        """
        conf_parser = Parser(self.logname)
        msg = { 'status': "", 'msg': "", 'changes': [] }

        try:
            Validator().check_config(config, self.logname)

        except Exception as err:
            msg['status'] = "error"
            msg['msg'] = (f"The new config did not pass the config validity "
                          f"check. {err}")
            return msg
        matches = self.config_hashes_matches(config)
        if matches:
            msg['status'] = "matches"
            msg['msg'] = (f"The new config and the stored configs are the same."
                            " No changes were made.")
        else:
            msg['status'] = "changed"
            msg['msg'] = "Changes have been found in the new config."
            changes = self.find_differences_in_configs(config, self.config_file)
            msg['changes'] = changes
        return msg


    def set_up_config_to_be_active(self, config):
        """ Helper to make config the new active config """
        conf_parser = Parser(self.logname)
        self.hashed_config = conf_parser.get_hash(OrderedDict(config))
        self.config_file = config
        links, p4_switches, switches, group_links = conf_parser.parse_config(config)
        dp_id_to_sw = self.associate_dp_id_to_swname(switches)
        parsed_config = {"links": links,
                         "p4_switches": p4_switches,
                         "switches": switches,
                         "group_links": group_links,
                         "dp_id_to_sw_name": dp_id_to_sw}
        return parsed_config


    def find_differences_in_configs(self, new_config, old_config):
        """ More fine grained check to find differences between configs and
            report changes back

        Args:
            new_config (dict): The new config to compare
            old_config (dict): The old config to compare with

        Returns:
            [str]: List of differences between the configs
        """
        changes = []

        if not self.config_hashes_matches(new_config['switch_matrix'], old_config['switch_matrix']):
            changes.append("Changes were found in the switch matrix")
        if not self.compare_hosts_matrix_hashes(new_config['hosts_matrix'],
                                                old_config['hosts_matrix']):
            changes.append("Changes were found in the hosts matrix")

        return changes


    def compare_hosts_matrix_hashes(self, new_hosts_matrix, old_hosts_matrix):
        """ Make a hash of the old and new hosts matrices and compares the
            hashes to see if a difference can be found

        Args:
            new_hosts_matrix (list): New hosts list to compare
            old_hosts_matrix (list): Old hosts list to compare

        Return:
            bool: Whether they match or not
        """
        conf_parser = Parser(self.logname)
        old_hosts_sorted = sorted(old_hosts_matrix, key=lambda k: k['name'])
        new_hosts_sorted = sorted(new_hosts_matrix, key=lambda k: k['name'])
        old_hosts_hash = conf_parser.get_hash(old_hosts_sorted)
        new_hosts_hash = conf_parser.get_hash(new_hosts_sorted)

        if old_hosts_hash == new_hosts_hash:
            return True
        return False


    def setup_logger(self, loglevel=logging.INFO,
                     logfile=DEFAULT_LOG_FILE, quiet=False):
        """ Setup and return the logger """

        logger = logging.getLogger(self.logname)
        log_handler = logging.FileHandler(logfile, mode='a+')
        log_handler.setFormatter(
            logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s',
                              '%b %d %H:%M:%S'))
        logger.addHandler(log_handler)

        logger.setLevel(loglevel)

        return logger
