#!/usr/bin/env python3
import sys, os, time, socket, re, copy
from netdevice import linux,ovs
import simplejson as json
import ipaddress
from binascii import hexlify, unhexlify
import random
try:
    # Python 2.
    from StringIO import StringIO
    # Python 3.
except ImportError:
    from io import StringIO

try:
    # Python 2.
    import urlparse
except ImportError:
    # Python 3.
    import urllib.parse as urlparse

class OvnHost(ovs.OvsHost):
    '''
    OvsHost is a linux host with OpenvSwitch installed. You can build the
    topology and run test on it.

    Now it integerate the docker and can connect the container automatically.
    '''
    def __init__ (self, server = None, **kwargs):
        '''
        Connect the host and start the OVS.
        '''
        kwargs["type"] = kwargs.get("type", "OVN")
        ovs.OvsHost.__init__(self, server, **kwargs)
        # If there is no controller, myself is the controler
        self.controller = kwargs.get("controller", None)
        self.tunnel_port = kwargs.get("tunnel_port", None)
        self.tunnel_ip = ipaddress.ip_interface(kwargs.get("tunnel_ip",
            None)).ip
        self.cmd("ip link set mtu 1600 dev %s" %(self.tunnel_port))

        # If tunnel_ip is given, initilize the northd/controller
        if not self.controller:
            #Myself is the controller
            self.start_northd(self.tunnel_ip)
            self.start_controller(self.tunnel_ip, self.tunnel_ip)
        else:
            # chassis
            self.start_controller(self.controller.tunnel_ip, self.tunnel_ip)

    #def __del__(self):
    #    '''
    #    Stop the service.
    #    '''
    #    if self["destroy_topology"]:
    #        self.uninit()
    #    linux.LinuxDevice.__del__(self)

    def start_northd (self, tunnel_ip, **kwargs):
        '''
        Start the northd service
        #ovn-northd创建数据库，并监听北向数据库:6641和南向数据库:6642
        '''
        self.tunnel_ip = tunnel_ip
        n = self.cmd('ps -ef | grep ovn-northd | egrep -v "grep" | wc -l',
                log_level = 4)
        if int(n) == 0:
            if "zh_CN" in self["LANG"]:
                self.log('#启动北向数据库并监听6641/6642端口.')
            else:
                self.log('#Start ovn-northd and list 6641/6642.')
            self.cmd("ovn-ctl start_northd")
            #Check the state of the nb/sb
            #self.cmd('ovn-nbctl show')
            self.cmd('ovn-sbctl show')
            self.cmd("ovn-nbctl set-connection ptcp:6641:%s" %(tunnel_ip))
            self.cmd("ovn-sbctl set-connection ptcp:6642:%s" %(tunnel_ip))

    def start_controller (self, server, client, **kwargs):
        '''
        #启动OVN controller 并和controller的南向数据库:6642相连
        '''
        self.tunnel_ip = client
        n = self.cmd('ps -ef | grep ovn-controller | egrep -v "grep" | wc -l',
                log_level = 4)
        if int(n) == 0:
            if "zh_CN" in self["LANG"]:
                self.log('#启动本地控制器并连接控制器6642端口.')
            else:
                self.log('#Start start_controller and connect controller:6642.')
            self.cmd("ovs-vsctl set Open_vSwitch . external-ids:system-id=%s"
                    %(self["name"]))
            self.cmd("ovs-vsctl set Open_vSwitch . external-ids:ovn-remote=tcp:%s:6642"
                    %(server))
            self.cmd("ovs-vsctl set Open_vSwitch . external-ids:ovn-encap-type=geneve")
            self.cmd("ovs-vsctl set Open_vSwitch . external-ids:ovn-encap-ip=%s"
                    %(client))
            self.cmd("ovn-ctl start_controller")
        self.log('\n')

    def stop_northd(self):
        '''
        Stop order is important: 1) the ovn controller, 2) ovn northd, 3) ovs
        Stop the ovn controller.
        '''
        n = self.cmd('ps -ef | grep ovn-northd | egrep -v "grep" | wc -l',
                log_level = 4)
        if int(n) > 0: # Stop ovn if it exist.
            #self.cmd('ovn-nbctl show')
            self.ls_del()
            self.lr_del()
            self.dhcp_options_del()
            self.address_set_del()
            self.acl_del()
            self.cmd("ovn-sbctl del-connection")
            self.cmd('ovn-sbctl show') # make sure all the connection torn down
            self.cmd("ovn-ctl stop_northd")

    def stop_controller(self):
        '''
        Stop order is important: 1) the ovn controller, 2) ovn northd, 3) ovs
        '''
        self.ovn_stop_vm(**{"type": "kvm"})
        self.ovn_stop_vm(**{"type": "container"})
        self.ovn_stop_vm(**{"type": "netns"})
        self.cmd("ovn-ctl stop_controller")

        #清空ovn 的配置, 不然init()里配置的external-ids会一直保留在这里。
        self.del_br()
        self.cmd("ovs-vsctl clear Open_vSwitch . external-ids")
        #self.cmd("ovs-ctl stop")
        self.log('\n')

    def lsp_add (self, ls_name, lsp_name, **kwargs):
        '''
        为逻辑交换机加入逻辑端口。如果虚拟交换机上配置了"subnet"参数，则为端口
        配置DHCP设置。
        '''
        self.cmd('ovn-nbctl lsp-add %s %s' %(ls_name, lsp_name))
        for k,v in kwargs.items():
            v = len(v.split()) > 1 and '"%s"' %(v) or v
            self.cmd('ovn-nbctl lsp-set-%s %s %s' %(k, lsp_name, v))
        if "addresses" not in kwargs:
            # Guess the peer lsp mac if not given
            if kwargs.get("type", None) == "router":
                my_dic = self._util_dictionary_parse(kwargs.get("options", None), ",")
                peer_lrp = my_dic.get("router-port", None)
                if not peer_lrp:
                    self.log("no route-port is given: %s." %(kwargs),
                            bg_color = "red")
                lrp_address = self.cmd("ovn-nbctl get logical_Router_port %s mac"
                        %(peer_lrp))
                self.cmd('ovn-nbctl lsp-set-addresses %s %s'
                        %(lsp_name, lrp_address))
            elif kwargs.get("type", None) == "localnet":
                self.cmd('ovn-nbctl lsp-set-addresses %s unknown' %(lsp_name))

        if ("dhcpv4-options" not in kwargs) and (not kwargs.get("type", None)):
            # If it's a vm/vif(empty string), 并且是连接路由器的端口
            # ，根据ls 上的"subnet" 设置找到cidr, 以及相应的dhcp_options
            controller = self.controller and self.controller or self
            subnet = self._get_ls_subnet(ls_name)
            #self.log('_get_ls_subnet() return: %s.' %(subnet))
            if subnet:
                long_cmd = 'ovn-nbctl --bare --columns=_uuid ' + \
                        'find dhcp_options cidr=%s' %(subnet)
                cidr_uuid = controller.cmd(long_cmd, log_level = 4).split()
                if not cidr_uuid:
                    #self.log('no dhcp_options found with cidr: %s.'
                    #        %(subnet), bg_color = "red")
                    return
                controller.cmd('ovn-nbctl lsp-set-dhcpv4-options %s %s'
                        %(lsp_name, cidr_uuid[0]))

    def lsp_del (self, ls_name, lsp_name, **kwargs):
        '''
        '''
        options = " ".join('%s %s' %(k,v) for k,v in kwargs.items())
        self.cmd('ovn-nbctl %s lsp-del %s %s' %(options, ls_name, lsp_name))
        # TODO: del the dhcpv4-options???

    def ls_add (self, name, *args, **kwargs):
        '''
        Add a OVN-L2网络:
        字典格式的参数：
            lsp1 = {"name": "ls1-vm1", "addresses": "00:00:00:00:00:01",
                    "port-security": "00:00:00:00:00:01"}
            node1.ls_add("ls1", lsp1, lsp2, lsp3)

        tuple格式的参数：
            lsp1 = ("ls1-vm1", "00:00:00:00:00:01")
            node1.ls_add("ls1", lsp1, lsp2, lsp3)
        '''
        if "zh_CN" in self["LANG"]:
            self.log('#创建一个逻辑分布式交换机: %s.' %(name))
        else:
            self.log('# Create a logical switch: %s.' %(name))

        self.cmd('ovn-nbctl ls-add %s' %(name))
        # Add ls port
        for lsp in args:
            if isinstance(lsp, dict):
                lsp_name = lsp.pop('name', 'invalid')
                self.lsp_add(name, lsp_name, **lsp)
            elif isinstance(lsp, tuple):
                self.lsp_add(name, lsp[0], lsp[1])

        if kwargs:
            #DHCP configuration
            other_config = " ".join('other_config:%s="%s"' %(k,v)
                    for k,v in kwargs.items())
            self.cmd('ovn-nbctl set logical_switch %s %s' %(name, other_config))
        #if "subnet" not in kwargs:
        #    # Guess subnet if not given
        #    subnet = self._get_ls_subnet(name)
        #    if subnet:
        #        self.log('# Guess the subnet: %s.' %(subnet))
        #        self.cmd('ovn-nbctl set logical_switch %s other_config:subnet=%s'
        #                %(name, subnet))
        self.log('\n')

    def ls_del (self, *args, **kwargs):
        '''
        del a OVN-L2网络
        '''
        if args:
            ls_list = args
        else:
            result = self.cmd("ovn-nbctl ls-list", log_level = 4)
            ls_list = StringIO(result).readlines()

        for ls in ls_list:
            #ls = ls.split()[1].strip("()")
            ls = ls.split()[0]
            #Deletes ACLs from entity.
            #self.cmd("ovn-nbctl acl-del %s" %(ls))
            self.cmd("ovn-nbctl --if-exists ls-del %s" %(ls))
        #self.cmd('ovn-nbctl --if-exists ls-del %s'
        #        %(" ".join('%s' %(k.strip()) for k in ls_list)))

    def lr_add (self, name, *args, **kwargs):
        '''
        Add a OVN-L3网络
            lrp1 = {"name": "ls1-vm1",
                    "ip": "192.168.0.1/24",
                    "mac": "02:d4:1d:8c:d9:ae"}
            node1.lr_add("ls1", lrp1, lrp2, lrp3)

            lrp1 = ("lrp1", "02:d4:1d:8c:d9:ae", "10.208.0.1/24"}
            node1.lr_add("ls1", lrp1, lrp2, lrp3)
        '''
        if "zh_CN" in self["LANG"]:
            self.log('#创建一个逻辑分布式路由器: %s.' %(name))
        else:
            self.log('#Create a logical router: %s.' %(name))

        self.cmd("ovn-nbctl lr-add %s" %(name))
        if kwargs:
            self.cmd('ovn-nbctl set Logical_Router %s %s'
                    %(name, " ".join('options:%s=%s' %(k,v) for k,v in kwargs.items())))

        for lrp in args:
            lrp_name = isinstance(lrp, dict) and lrp["name"] or lrp[0]
            lrp_mac = isinstance(lrp, dict) and lrp["mac"] or lrp[1]
            ip = isinstance(lrp, dict) and lrp["ip"] or lrp[2]
            #sanity check: check if netmask is given
            ip_sanity_check = ipaddress.ip_interface(ip)
            if (ip_sanity_check.network.prefixlen == ip_sanity_check.max_prefixlen):
                self.log("Warning: interface ip %s has no netmask." %(ip),
                        bg_color = "yellow")
                raise Exception('interface ip %s has no netmask.' %(ip))
            self.cmd("ovn-nbctl lrp-add %s %s %s %s" %(name, lrp_name, lrp_mac, ip))
        self.log('\n')

    def lr_del (self, *args, **kwargs):
        '''
        del a OVN-L3网络
        '''
        if args:
            lr_list = args
        else:
            result = self.cmd("ovn-nbctl lr-list", log_level = 4)
            lr_list = StringIO(result).readlines()

        for lr in lr_list:
            #lr = lr.split()[1].strip("()")
            lr = lr.split()[0].strip()
            self.cmd("ovn-nbctl --if-exists lr-del %s" %(lr))

    def dhcp_options_create (self, cidr, **kwargs):
        '''
        创建一个dhcp server
        '''
        if "zh_CN" in self["LANG"]:
            self.log('#配置一个DHCP options.')
        else:
            self.log('# Create a DHCP options.')

        options = ""
        if kwargs:
            #DHCP configuration
            options = " ".join('"%s"="%s"' %(k,v) for k,v in kwargs.items())

        #dhcp-options-create cidr [key=value]
        #dhcp-options-set-options dhcp-option [key=value]...
        cidr_uuid = self.cmd('ovn-nbctl create dhcp_options cidr=%s options=\'%s\''
                %(cidr, options))
        self.log('\n')
        return cidr_uuid.strip()

    def dhcp_options_del (self, *args, **kwargs):
        '''
        创建一个dhcp server
        '''
        if args:
            dhcp_options_list = args
        else:
            result = self.cmd("ovn-nbctl --bare --columns=_uuid list dhcp_options",
                    log_level = 4)
            dhcp_options_list = result.split()
            #self.log("result: %s" %(result))
            #self.log("dhcp_options_list: %s" %(dhcp_options_list))
        for d in dhcp_options_list:
            self.cmd('ovn-nbctl dhcp-options-del %s' %(d))

    def address_set_create (self, name, addresses, **kwargs):
        '''
        创建一个dhcp server
        '''
        if "zh_CN" in self["LANG"]:
            self.log('#配置一个Address_Set .')
        else:
            self.log('# Create an Address_Set .')

        cidr_uuid = self.cmd(
                'ovn-nbctl create Address_Set name=%s addresses="%s"'
                %(name, addresses))
        self.log('\n')

    def address_set_del (self, *args, **kwargs):
        '''
        创建一个dhcp server
        '''
        if args:
            address_set_list = args
        else:
            #result = self.cmd("ovn-nbctl --bare --columns=_uuid list Address_Set ",
            result = self.cmd("ovn-nbctl --bare --columns=name list Address_Set ",
                    log_level = 4)
            address_set_list = result.split()

        #for add in address_set_list:
        #    self.cmd('ovn-nbctl destroy Address_Set %s' %(add))
        self.cmd('ovn-nbctl destroy Address_Set %s'
                %(" ".join('%s' %(k.strip()) for k in address_set_list)))

    def acl_add (self, entity, direction, priority, match, verdict, **kwargs):
        '''
        创建一个ACL: ovn-nbctl acl-add entity direction priority match verdict
        '''
        if "zh_CN" in self["LANG"]:
            self.log('#配置一个ACL .')
        else:
            self.log('# Create an ACL .')

        cidr_uuid = self.cmd(
                'ovn-nbctl acl-add %s %s %s match verdict'
                %(entity, direction, priority))
        self.log('\n')

    def acl_del (self, *args, **kwargs):
        '''
        创建一个ACL
        '''
        if args:
            address_set_list = args
        else:
            #result = self.cmd("ovn-nbctl --bare --columns=_uuid list Address_Set ",
            result = self.cmd("ovn-nbctl --bare --columns=name list Address_Set ",
                    log_level = 4)
            address_set_list = result.split()

        #for add in address_set_list:
        #    self.cmd('ovn-nbctl destroy Address_Set %s' %(add))
        self.cmd('ovn-nbctl destroy Address_Set %s'
                %(" ".join('%s' %(k.strip()) for k in address_set_list)))

    def ovn_bridge_mappings (self, network, bridge_name):
        '''
        配置虚拟网络出接口和本地物理网络的映射:

            ovn-bridge-mappings 指定了网络名称和实际网桥的映射关系, 必须在网关
            路由器的选项 options:chassis=controller 指定的 chassis上执行。
        
            如果有多于一个的物理网络，必须将新的mapping 关系加到老的上面，而不
            能简单的替换，参考：

            ~/ovn-21.03.0/: grep -r "ovn-bridge-mappings" *
            external-ids:ovn-bridge-mappings=phys-11:br-phys11,phys-21:br-phys21
        '''
        external_ids = self.cmd("ovs-vsctl get Open_vSwitch . external_ids")
        my_dic = self._util_dictionary_parse(external_ids, ", ")
        ovn_bridge_mappings = my_dic.get("ovn-bridge-mappings", "").strip('"')
        ovn_bridge_mappings += "%s%s:%s"%(ovn_bridge_mappings and "," or "",
                network, bridge_name)
        self.cmd("ovs-vsctl set Open_vSwitch . external-ids:ovn-bridge-mappings=%s"
                %(ovn_bridge_mappings))

    def ovn_start_vm (self, name, nics = [], **kwargs):
        '''
        创建一个虚拟机@name, 其中有几个网卡nics. 将这个主机的网卡连接到逻辑交
        换机上(逻辑交换机由网卡参数定义)。
        '''
        vm_type = kwargs.get("type", "kvm")
        if "zh_CN" in self["LANG"]:
            self.log('#创建一个虚拟机: %s(类型: %s).' %(name, vm_type))
        else:
            self.log('#Create a vm: %s(type: %s).' %(name, vm_type))

        if vm_type == "kvm":
            # start vm and add all the nic to ls
            self.ovs_start_kvm_vm(name, *nics, **kwargs)
            for nic in nics:
                if nic.get("ls", None):
                    # 如果配置交换机，将虚拟机的每张网卡连接到逻辑交换机上。
                    self._add_nic_to_ls(nic, nic["ls"], nic.get("lsp", None))
        elif vm_type == "container":
            nic = nics[0] #Only support 1 nic for container now
            ofport = self.ovs_start_container("br-int",
                    kwargs.get("image", "centos"), name, **nic)
            nic["port"]= ofport # get the port set by "ovs-docker add-port"
            self._add_nic_to_ls(nic, nic["ls"], nic.get("lsp", None))
            if not nic.get("ip", None): #DHCP
                self.cmd("docker exec -it %s dhclient" %(name)) # no-wait
        elif vm_type == "netns":
            nic = nics[0]
            self.ovs_start_netns_vm("br-int", name, nic)
            self._add_nic_to_ls(nic, nic["ls"], nic.get("lsp", None))

            if not nic.get("ip", None):
                # Get IP by dhcp if ip is not given
                self.cmd("dhclient -r && ip netns exec %s dhclient" %(name))
                #dhclint不要使用no-wait, 我们有可能要用主机上的某个IP做测试，如果
                #返回的时候它还没有DHCP成功的话可能影响测试，很难查。
                #self.cmd("dhclient -r && dhclient -nw") # no-wait
                self.cmd("dhclient -r && dhclient")
                cmd = "ip -o -4 addr list %s | awk '{print $4}'" %(nic["port"])
                nic["ip"] = self.cmd("ip netns exec %s %s" %(name, cmd)).strip()
            self.log('\n')

    def ovn_stop_vm (self, *args, **kwargs):
        '''
        '''
        vm_type = kwargs.get("type", "kvm")
        if vm_type == "kvm":
            self.ovs_stop_kvm_vm(*args, **kwargs)
        elif vm_type == "container":
            self.ovs_stop_container(*args, **kwargs)
        elif vm_type == "netns":
            self.ovs_stop_netns_vm("br-int", *args, **kwargs)

    def _get_ls_subnet (self, ls, **kwargs):
        '''
        查询该逻辑交换机对应的路由器端口的子网配置。
        '''
        #if self.controller:
        #    self.log("This operation is only permitted on controller.")
        #    return None

        # 如果交换机上配置了subnet, 则使用该subnet.
        long_cmd = 'ovn-nbctl --bare --columns=other_config find ' +\
                'logical_switch name=%s' %(ls)
        result = self.cmd(long_cmd, log_level = 4)
        if "subnet=" in result:
            other_config = self._util_dictionary_parse(result, ",")
            #self.log("other_config: %s" %(other_config))
            subnet = other_config.get("subnet", None)
            if (subnet):
                return subnet

        # 如果交换机上没有配置subnet, 则先找到该交换机连接的路由路口，获得该
        # 端口的子网.
        lsps_in_ls = self.cmd('ovn-nbctl lsp-list %s' %(ls), log_level = 4)
        long_cmd = 'ovn-nbctl --bare --columns=name find ' +\
                'Logical_Switch_Port type=router'
        all_route_lsp = self.cmd(long_cmd, log_level = 4)
        peer_lrp = None
        #self.log("lsps_in_ls: %s" %(lsps_in_ls))
        for lsp in all_route_lsp.split():
            #self.log("lsp: %s" %(lsp))
            if lsp in lsps_in_ls:
                lsp_options = self.cmd('ovn-nbctl lsp-get-options %s' %(lsp),
                        log_level = 4)
                options_dic = self._util_dictionary_parse(lsp_options, ",")
                #self.log("options_dic: %s" %(options_dic))
                peer_lrp = options_dic.get("router-port", None)
                #self.log("peer_lrp: %s" %(peer_lrp))
                if peer_lrp:

                    long_cmd = 'ovn-nbctl --bare --columns=networks find ' + \
                            'Logical_Router_Port name=%s' %(peer_lrp)
                    ip_lrp = self.cmd(long_cmd, log_level = 4)
                    #self.log("ip_lrp: %s" %(ip_lrp))
                    ipaddr = ipaddress.ip_interface(ip_lrp.strip())
                    #self.log("ipaddr: %s" %(ipaddr))
                    return str(ipaddr.network)
        return None

    def _util_dictionary_parse (self, intput_string, seperator = ', '):
        '''
        解析由intput_string 描述的字典，可以指定不同项之间的分隔符，但是key和
        value之间必须由=分隔
        intput_string: "{a=a1, b=b2, c=c2}"
        output: dict: {"a": "a1", "b": "b2", "c": "c2"}
        '''
        output_dic = {}
        params = intput_string.strip('\s\{\}').split(seperator)

        if "=" not in params[0]:
            output_dic["type"] = params.pop(0)
        for attribute in params:
            if ("=" in attribute):
                k,v = attribute.split("=", 1)
                output_dic[k.strip()] = v.strip()
            else:
                output_dic[attribute] = ""
        return output_dic

    def _add_nic_to_ls (self, nic, ls, lsp = None):
        '''
        将一个nic 连接到OVN的逻辑交换机上：方法就是使nic["port"](和nic相连
        的ovs interface) 上的external_ids:iface-id和lsp 同名。
        '''
        #解析interface: nic["port"] 上面挂的external_id
        external_id = {}
        result = self.cmd('ovs-vsctl get interface %s external_ids'
                %(nic["port"]), log_level = 4)
        for item in result.strip('{} ').split(","):
            if ("=" in item):
                k,v = item.split("=", 1)
                external_id[k.strip()] = v.strip()
        #self.log("external_id: %s" %(external_id))

        # If there is iface-id, use it, or use lsp, or create a new lsp name
        controller = self.controller and self.controller or self
        iface_id = external_id.get("iface-id", None)
        lsp = iface_id and iface_id.strip() or lsp
        lsp = lsp and lsp or "%s-%s" %(ls, nic["port"])

        #如果配置没有提供IP地址，则设置dynamic选项。建议虚拟机总是不配置IP,因
        #为虚拟机的IP不是在外部配置，而是要登录到虚拟机内部配置的, 应该总是为
        #其设置DHCP
        mac = external_id.get("attached-mac", nic["mac"])
        address = "%s %s" %(nic["mac"],
                nic.get("ip", None) and nic["ip"] or "dynamic")
        controller.lsp_add(ls, lsp, addresses = address)
        if not iface_id:
            self.cmd('ovs-vsctl set Interface %s external_ids:iface-id=%s'
                    %(nic["port"], lsp))



if __name__ == '__main__':
    '''
    '''
    controller = ovn.OvnHost("ssh://root:centos@192.168.199.5",
            log_color = "blue")
    node1 = ovn.OvnHost("ssh://root:centos@192.168.199.6",
            controller = controller, log_color = "red")
    node2 = ovn.OvnHost("ssh://root:centos@192.168.199.7",
            controller = controller, log_color = "purple")

    controller.cmd("ovn-sbctl show")

    vm1 = {"name": "vm1", "ip": "10.10.10.11/24", "mac": "00:00:00:00:00:03",
            "gw": "10.10.10.1"}
    vm2 = {"name": "vm2", "ip": "10.10.10.12/24", "mac": "00:00:00:00:00:04",
            "gw": "10.10.10.1"}

    lsp1 = {"name": "ls1-vm1",
            "addresses": "00:00:00:00:00:01",
            "port-security": "00:00:00:00:00:01"}
    lsp2 = {"name": "ls1-vm2",
            "addresses": "00:00:00:00:00:02",
            "port-security": "00:00:00:00:00:02"}
    controller.ls_add("ls1", lsp1, lsp2, lsp3)
    controller.cmd("ovn-nbctl show")

    controller.ovn_start_netns_vm("ls1", "ls1-vm1", "test1", vm1)
    node1.ovn_start_netns_vm("ls1", "ls1-vm2", "test2", vm2)

