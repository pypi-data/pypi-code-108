#!/usr/bin/env python3
import sys, os, time, socket, re, copy
from netdevice import linux
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

ovstools_script = '''
#!/bin/bash
#Transfer the ip address from $bridge to $physicial interface.
# INPUT:
#     br: bridge name
#     ifname: interface name
# OUTPUT:
#     null
# sh .netdevice_ovstools.sh takeover eno1 br0 eno1
function ovsif_takeover()
{
    local ifname=$1
    local br=$2
    local port=$3
    local ip4=""
    local ip6=""
    #local mac=""
    local route=""

    ip4=$(ip -o -4 addr list $ifname | awk '{print $4}')
    # TODO:IPV6
    ip6=$(ip -o -6 addr list $ifname | awk '{print $4}')
    #mac=$(ip link show $ifname | grep "link/ether" | awk '{print $2}')
    IFS=$'
'
    route=($(ip route show | grep $ifname | grep -v link | sed "s/$ifname/$br/g"))

    echo "#Take over $ip4 from $ifname to $br($port)."
    ip addr flush dev $ifname
    echo "ip addr flush dev $ifname"

    # Add the physicial interface to the bridge $br
    ovs-vsctl --may-exist add-port $br $port
    echo "ovs-vsctl --may-exist add-port $br $port"

    #if [[ $ifname == $port ]]
    #then
    #    # Add the physicial interface to the bridge $br
    #    ovs-vsctl add-port $br $ifname
    #    echo "ovs-vsctl add-port $br $ifname"
    #fi

    #ovs-vsctl set bridge $br other_config:hwaddr=$mac
    ip link set $br up
    echo "ip link set $br up"
    if [ -n "$ip4" ]; then
        ip address add $ip4 dev $br
        echo "ip address add $ip4 dev $br"
    else
        echo "ip4 is empty, ignore..."
    fi

    # transfer the route from $ifname to $br
    for line in ${route[@]};
    do
        #echo "ip route add $line"
        eval ip route add $line
    done

    return 0
}

#Restore the ip address from $physicial interface to $bridge.
# INPUT:
#     br: bridge name
#     ifname: interface name
# OUTPUT:
#     null
function ovsif_restore()
{
    local ifname=$1
    local br=$2
    local port=$3
    local ip4=""
    local ip6=""
    local route=""

    ip4=$(ip -o -4 addr list $br | awk '{print $4}')
    # TODO:IPV6
    ip6=$(ip -o -6 addr list $br | awk '{print $4}')
    IFS=$'
'
    route=($(ip route show | grep $br | grep -v link | sed "s/$br/$ifname/g"))

    echo "#restore $ip4 from $br to $ifname, del $port from $br."
    ip addr flush dev $br
    echo "ip addr flush dev $br"
    ovs-vsctl del-port $br $port
    echo "ovs-vsctl del-port $br $port"
    ip address add $ip4 dev $ifname
    echo "ip address add $ip4 dev $ifname"
    
    # transfer the route from $ifname to $br
    for line in ${route[@]};
    do  
        #echo "ip route add $line"
        eval ip route add $line
    done
    
    return 0
}

function ovsif_help()
{
    echo "Usage:"
    echo "    sh $0 takeover br ifname."
    echo "    sh $0 restore br ifname."
}

# The main function for ovsif takeover
# INPUT: $@: All the parameters
# OUTPUT: null
# RETURN: 0 if succeed, or else
function main()
{
    local params=""

    if test $# -eq 0
    then
        ovsif_help
        return 0
    fi

    local pid_num_of_ovs=0
    pid_num_of_ovs=$(ps -ef | grep -w ovs-vswitchd | grep -v grep | wc -l)
    if test $pid_num_of_ovs -le 0
    then
        echo "It seems that OVS is not running. Please start it at first."
        return 0
    fi

    case "$1" in
        takeover)
            shift
            ovsif_takeover "$@" ;;
        restore)
            shift
            ovsif_restore "$@" ;;
        *)
            shift
            ovsif_help ;;
    esac
}

# Variables must be declared explicitly
set -u
main "$@"
exit $?

# vim: ts=4 sw=4 cindent expandtab
'''


class OvsHost(linux.LinuxDevice):
    '''
    OvsHost is a linux host with OpenvSwitch installed. You can build the
    topology and run test on it.

    Now it integerate the docker and can connect the container automatically.
    '''
    def __init__ (self, server = None, **kwargs):
        '''
        Connect the host and start the OVS.
        '''
        kwargs["type"] = kwargs.get("type", "OVS")
        linux.LinuxDevice.__init__(self, server, **kwargs)
        self.devices = []
        self.macs = []

        # start the docker if it's not running
        n = self.cmd('ps -ef | grep ovs-vswitchd | egrep -v "grep" | wc -l',
                log_level = 4)
        if int(n) == 0:
            self.cmd('ovs-ctl start')

        # Get all the pnic list
        cmd = "ls -l /sys/class/net/ | egrep -v 'virtual|total' " +\
                "| awk '{print $9}'"
        self.nics = self.cmd(cmd, log_level = 4).split()
        #self.log("host's phicial nics: %s" %(" ".join(k for k in self.nics)))

    def __del__(self):
        '''
        Get the trace file.
        Don't stop the OVS or docker.
        '''
        #if (self["vlog"] > 0):
        #    #self.get_file('/usr/local/var/log/openvswitch/ovsdb-server.log',
        #    #        "%s_ovsdb-server.log" %(self["name"]))
        #    self.get_file('/usr/local/var/log/openvswitch/ovs-vswitchd.log',
        #            "%s_ovs-vswitched.log" %(self["name"]))
        linux.LinuxDevice.__del__(self)

    def add_br (self, name, **kwargs):
        '''
        ovs-vsctl add br xxx
        ovs-vsctl add port brxxx xxx
        '''
        #log
        if "zh_CN" in self["LANG"]:
            self.log('#创建一个网桥: %s.' %(name))
        else:
            self.log('#Create a bridge: %s.' %(name))

        command = 'ovs-vsctl --may-exist add-br %s' %(name)
        if kwargs:
            command += ' -- set bridge %s ' %(name)
            command += " ".join('%s=%s' %(k,v) for k,v in kwargs.items())
        self.cmd(command)

    def del_br (self, *args, **kwargs):
        '''
        Delete the bridge and all the connected devices(containers).

        If bridge name is not given, delete all the bridges.
        '''
        # delete all the bridges in the OVS
        bridges = args and args or self.cmd("ovs-vsctl list-br")
        for b in StringIO(bridges).readlines():
            b = b.strip()
            ports = self.cmd("ovs-vsctl list-ports %s" %(b), log_level=4)
            for p in StringIO(ports).readlines():
                self.del_port(b, p.strip())
            self.cmd("ovs-vsctl del-br %s" %(b))

    def add_port (self, bridge_name, name, **kwargs):
        '''
        ovs-vsctl add port brxxx xxx.
        If it's a physicial nic, call take_over_interface() script.
        '''
        if (kwargs.get("type", "normal") == "normal") and \
                (name in self.nics):
            #If it's a normal interface, take over it
            self.ovs_takeover_interface(bridge_name, name)
            return None
        else:
            command = 'ovs-vsctl --may-exist add-port %s %s'\
                    %(bridge_name, name)
            if kwargs:
                command += ' -- set Interface %s' %(name)
                command += " ".join('%s=%s' %(k,v) for k,v in kwargs.items())
            self.cmd(command)

    def add_bond (self, bridge_name, bond_name, *args, **kwargs):
        '''
        Add bond.
        '''
        ip = kwargs.pop("ip", []) #ip is private paramater.
        for p in args:
            self.cmd("ip addr flush dev %s" %(p))
        cmd = "ovs-vsctl add-bond %s %s" %(bridge_name, bond_name)
        cmd += " " + " ".join(args)
        cmd += " " + " ".join('%s=%s' %(k,v) for k,v in kwargs.items())
        self.cmd(cmd)

        if ip:
            # Configure the ip address for the address for route
            self.cmd('ip link set %s up' %(bridge_name))
            self.cmd('ip address add %s dev %s' %(ip, bridge_name))

    def del_port (self, bridge_name, *args, **kwargs):
        '''
        Delete the ports given.
        '''
        for port in args:
            p = port.strip()
            if (p in self.nics):
                # Restore the "phisical" interface
                self.ovs_no_takeover_interface(bridge_name, p)
            else:
                self.cmd("ovs-vsctl del-port %s %s" %(bridge_name, p))

    def set_interface (self, name, **kwargs):
        '''
        '''
        command = 'ovs-vsctl set Interface %s ' %(name)
        command += " ".join('%s=%s' %(k,v) for k,v in kwargs.items())
        self.cmd(command)

    def get_interface (self, interface, attribute = None):
        '''
        Get a self-port which connect to the kwargs["name"]
        '''

        if attribute:
            result = self.cmd("ovs-vsctl get interface %s %s"
                    %(interface, attribute))
            return result.strip()

        i = {}
        result = self.cmd("ovs-vsctl list interface %s" %(interface),
                log_level=4)
        for p in StringIO(result).readlines():
            k,v = p.split(":", 1)
            i[k.strip()] = v.strip()

        #return attribute and i.get(attribute, None) or i
        return i

    def add_flow (self, bridge_name, *args, **kwargs):
        '''
        Add some flows to ofproto
        '''
        for table in args:
            table = filter(lambda x: (x.strip()) and (x.strip()[0] != '#'),
                    StringIO(table.strip()).readlines())
            for l in table:
                # remove the line starting with '#'
                l = l.strip()
                if l[0] !=  "#":
                    self.cmd('ovs-ofctl add-flow %s %s' %(bridge_name, l))
        return None

    def ovs_add_vrouter (self, bridge_name, gw, *args):
        '''
        Add a vrouter which will respond with the gateway ip.
        '''
        #if self["fail-mode"] != "secure":
        if self.cmd("ovs-vsctl get-fail-mode %s" %(bridge_name)).strip() != "secure":
            #Don't need configure gateway explicitly in standalone mode.
            return

        #self.log("gw mac: %s" %(gw["mac"]))
        #self.log("mac: %s" %(self.macs))
        if (gw["mac"] not in self.macs):
            # gw is not on this node, Add it as if it's on this node.
            ipaddr = ipaddress.ip_interface(gw["ip"]).ip
            self.add_flow(bridge_name,
                    'priority=1000,arp,arp_tpa=%s,arp_op=1,actions=move:"NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[]",mod_dl_src:"%s",load:"0x02->NXM_OF_ARP_OP[]",move:"NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[]",load:"0x%s->NXM_NX_ARP_SHA[]",move:"NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[]",load:"0x%s->NXM_OF_ARP_SPA[]",in_port'%(ipaddr,
                        gw["mac"],
                        re.sub(r":", "", gw["mac"]),
                        "".join(f"{i:02x}" for i in ipaddr.packed)),
                    'priority=1000,icmp,nw_dst=%s,icmp_type=8,icmp_code=0,actions=push:"NXM_OF_ETH_SRC[]",push:"NXM_OF_ETH_DST[]",pop:"NXM_OF_ETH_SRC[]",pop:"NXM_OF_ETH_DST[]",push:"NXM_OF_IP_SRC[]",push:"NXM_OF_IP_DST[]",pop:"NXM_OF_IP_SRC[]",pop:"NXM_OF_IP_DST[]",load:"0xff->NXM_NX_IP_TTL[]",load:"0->NXM_OF_ICMP_TYPE[]",in_port' %(ipaddr))

        for d in args:
            #self.log("d: %s" %(d))
            if d.get("mac", None) and (d['mac'] in self.macs):
                #self.log("d: %s" %(d))
                # ONly change the mac and ttl on the same host.
                self.add_flow(bridge_name,
                    "priority=1000,ip,nw_dst=%s,action=mod_dl_src:%s,"
                    "mod_dl_dst:%s,dec_ttl,output:%s"
                    %(d["ip"].split("/")[0], gw["mac"], d["mac"], d["ofport"]))

    def ovs_set_next_hop (self, bridge_name, out_if, *args):
        '''
        It's the same as add_vtep(), only different in the name.
        '''
        #if self["fail-mode"] != "secure":
        if self.cmd("ovs-vsctl get-fail-mode %s" %(bridge_name)).strip() != "secure":
            #Don't need configure out_if explicitly in standalone mode.
            return
        for arg in args:
            ipaddr = ipaddress.ip_interface(arg["ip"]).ip
            vxlan_port = self.get_interface(out_if["name"], "ofport")
            self.add_flow(bridge_name,
                    "priority=1000,arp,arp_tpa=%s,actions=output:%s"
                    %(ipaddr, vxlan_port),
                    "priority=1000,ip,nw_dst=%s,actions=output:%s" 
                    %(ipaddr, vxlan_port))

    def ovs_ping_test (self, src, *args, **kwargs):
        '''
        depreated: Dont' use it.
        '''
        for dst in args:
            try:
                dstip = ipaddress.ip_interface(
                        isinstance(dst, dict) and dst["ip"] or dst)
                dst = dstip.ip
            except:
                #self.log("a domain name: %s?" %(dst))
                pass

            if src["type"] == "container":
                result = self.cmd('docker exec -it %s ping %s -c 1'
                        %(src["name"], dst))
            elif src["type"] == "vm" or src["type"] == "kvm":
                #result = self.cmd('sshpass -p %s ssh %s@%s ping -c 1 %s')
                result = self.cmd('ssh %s ping -c 1 %s' %(src["name"], dst))
            elif src["type"] == "netns":
                result = self.cmd('ip netns exec %s ping -c 1 %s'
                        %(src["name"], dst))
            else:
                self.log("ERROR: don't support the type %s!"
                        %(src["type"]), bg_color = "purple")
                return False

            if "received, 0% packet loss," in result:
                self.log("PASS: %s ping %s!" %(src["name"], dst),
                        bg_color = "green")
            else:
                self.log("FAIL: %s ping %s!" %(src["name"], dst),
                        bg_color = "red")

    def ovs_takeover_interface (self, bridge, ifname, port = None):
        '''
        takeover the ip from @ifname to @bridge(@port)
        '''
        filename = '.netdevice_ovstools.sh'
        if self.cmd("[ -f ~/%s ] || echo no" %(filename)).strip() == "no":
            with open(filename, 'w') as f:
                f.write(ovstools_script)
            self.put_file(filename, "~/")

        self.cmd("sh ~/%s takeover %s %s %s" %(filename,
            ifname, bridge, port and port or ifname))

    def ovs_no_takeover_interface (self, bridge, ifname, port = None):
        '''
        restore the ip from @bridge(@port) to @ifname
        '''
        filename = ".netdevice_ovstools.sh"
        if self.cmd("[ -f ~/%s ] || echo no" %(filename)).strip() == "no":
            with open(filename, 'w') as f:
                f.write(ovstools_script)
            self.put_file(filename, "~/")

        self.cmd("sh ~/%s restore %s %s %s" %(filename,
            ifname, bridge, port and port or ifname))

    def ovs_start_kvm_vm (self, name, *args, **kwargs):
        '''
        caculate the qemu command by kwargs.

        After start a vm, set somthing about external_ids: attached-mac,
        iface-id, iface-status, vm-id, etc.
        '''
        vm = {}
        vm["-m"] = kwargs.get("-m", "512M")
        vm["-smp"] = kwargs.get("-smp", "sockets=1,cores=1")
        vm["-hda"] = kwargs.get("-hda", "/media/qemu/vm1_centos73.img")
        vm["-vnc"] = kwargs.get("-vnc", ":1")
        vm["-name"] = kwargs.get("-name", name)
        vm["-cpu"] = kwargs.get("-cpu", "host")
        vm["-boot"] = kwargs.get("-boot", "c")
        vm["-pidfile"] = kwargs.get("-pidfile", "/tmp/%s.pid" %(name))
        vm["-enable-kvm"] = kwargs.get("-enable-kvm", "")
        vm["-object"] = kwargs.get("-object",
            "memory-backend-file,id=mem,size=%s,mem-path=/dev/hugepages,share=on"
            %(vm["-m"]))
        vm["-numa"] = kwargs.get("-numa", "node,memdev=mem")
        vm["-mem-prealloc"] = kwargs.get("-mem-prealloc", "")

        cmd = vm.get("mask", None) and ("taskset %s " %(vm["mask"])) or ""
        cmd += "qemu-system-x86_64"
        for k,v in vm.items():
            if k[0] == "-": #kvm parameter start with "-"
                cmd += ' %s %s' %(k,v)
        for nic in args:
            # Add the nic
            net_id = "%s_%s" %(name, nic["port"])
            #net_id = "net0"
            cmd += ' -netdev tap,ifname=%s,br=%s,script=no,downscript=/etc/ovs-br-int-ifdown,id=%s,vhost=on,vhostforce=on,queues=4' \
                    %(nic["port"], nic.get("bridge", "br-int"), net_id)
            cmd += ' -device virtio-net-pci,netdev=%s,mac=%s,vectors=10,mq=on' \
                    %(net_id, nic["mac"])

        # 2)start the qemu: tap mode need to start the qemu at frist,
        # vhostuser need to start the ovs-port at first. 
        tmp = self.cmd("%s -daemonize" %(cmd))

        for nic in args:
            self.cmd('ip link set %s up' %(nic["port"]))
            self.cmd('ovs-vsctl add-port %s %s'
                    %(nic.get("bridge", "br-int"), nic["port"]))
            self.set_interface(nic["port"],
                **{"external_ids:attached-mac": nic["mac"],
                   "external_ids:iface-id": nic["lsp"],
                   "external_ids:iface-status": "active",
                   "external_ids:vm-id": name})

    def ovs_stop_kvm_vm (self, *args, **kwargs):
        '''
        Power off the virtual machine from this host.
        从这台主机上将给定的虚拟机关机。
        '''
        for vm in args:
            #u = urlparse.urlparse(vm)
            #self.cmd('sshpass -p %s ssh %s@%s shutdown now' %(u.password,
            #    u.username, u.hostname))
            self.cmd('ssh %s shutdown now' %(vm))

    def ovs_start_container (self, bridge_name, container_image,
            container_name = "con1", **nic):
        '''
        Create a container and connect it to the bridge: bridge_name.
        '''
        # start the docker if it's not running
        n = self.cmd('ps -ef | grep dockerd | egrep -v "grep" | wc -l',
                log_level = 4)
        if int(n) == 0:
            self.cmd('systemctl start docker')

        #创建容器, 设置net=none可以防止docker0默认网桥影响连通性测试
        self.cmd('docker run --privileged -d --name %s --net=none -v /tmp:/tmp -it %s' %(container_name, container_image))

        name = "eth1"
        cmd = 'ovs-docker add-port %s %s %s' %(bridge_name, name, container_name)
        if (nic.get("ip", None)):
            #sanity check: check if netmask is given
            ip_sanity_check = ipaddress.ip_interface(nic["ip"])
            if (ip_sanity_check.network.prefixlen == ip_sanity_check.max_prefixlen):
                self.log("Warning: interface ip %s has no netmask." %(nic["ip"]),
                        bg_color = "yellow")
                raise Exception('interface ip %s has no netmask.' %(nic["ip"]))
            cmd += " --ipaddress=%s" %(nic["ip"])
        if (nic.get("mac", None)):
            cmd += " --macaddress=%s" %(nic["mac"])
        if (nic.get("gw", None)):
            cmd += " --gateway=%s" %(nic["gw"])
        if (nic.get("mtu", None)):
            cmd += " --mtu=%s" %(nic["mtu"])
        self.cmd(cmd)

        # Configure vlan on self-port if the device has vlan configured.
        ovs_of_port = self._ovs_get_container_port(container_name)
        if (nic.get("vlan", None)):
            self.cmd('ovs-vsctl set port %s tag=%d' %(ovs_of_port, nic["vlan"]))
        return ovs_of_port

    def ovs_stop_container (self, *args, **kwargs):
        '''
        删除本node上的container, 如果没有给定名字，则删除所有的container,
        '''
        #self.cmd("docker ps -qa")
        n = self.cmd('ps -ef | grep dockerd | egrep -v "grep" | wc -l',
                log_level = 4)
        if int(n) > 0:
            if args:
                containers = args
            else:
                result = self.cmd("docker ps -qa", log_level = 4)
                containers = StringIO(result).readlines()
            for c in containers:
                c = c.strip()
                self.cmd('docker stop %s' %(c))
                self.cmd('docker rm %s' %(c))

    def ovs_start_netns_vm (self, bridge_name, namespace, nic):
        '''
        创建一个ovs internal port(vnic), 为其配置IP/MAC/GW/VLAN, 并将其加入
        namespace, 模块一个主机名为namespace, 网卡为nic的虚拟机.
        '''
        #创建一个vnic, 并将其配置到namespace命名空间
        self.cmd("ovs-vsctl add-port br-int %s -- set interface %s type=internal"
                %(nic["port"], nic["port"]))
        self.cmd("ip netns add %s" %(namespace))
        self.cmd("ip link set %s netns %s" %(nic["port"], namespace))

        #为该vnic 配置IP/MAC/GW/vlan 等。
        self.cmd("ip netns exec %s ip link set %s address %s"
                %(namespace, nic["port"], nic["mac"]))
        self.cmd("ip netns exec %s ip link set %s up"
                %(namespace, nic["port"]))
        if nic.get("ip", None):
            #sanity check: check if netmask is given
            ip_sanity_check = ipaddress.ip_interface(nic["ip"])
            if (ip_sanity_check.network.prefixlen == ip_sanity_check.max_prefixlen):
                self.log("Warning: interface ip %s has no netmask." %(nic["ip"]),
                        bg_color = "yellow")
                raise Exception('interface ip %s has no netmask.' %(nic["ip"]))

            # If ip is given, set ip.
            self.cmd("ip netns exec %s ip addr add %s dev %s"
                    %(namespace, nic["ip"], nic["port"]))
            if nic.get("gw", None):
                # If gw is given, set the default route.
                self.cmd("ip netns exec %s ip route add default via %s dev %s"
                        %(namespace, nic["gw"], nic["port"]))

    def ovs_stop_netns_vm (self, bridge_name, *args, **kwargs):
        '''
        删除本node上的netns 及其关联的ovs port, 如果没有给定名字，则删除所有的
        netns及其关联的ovs port,
        '''
        if args:
            netns = args
        else:
            result = self.cmd("ip netns list", log_level = 4)
            netns = StringIO(result).readlines()
        #self.log("netns: %s" %(netns))

        for ns in netns:
            # Delete the namespace and related ovs port.
            ns = ns.split()[0].strip()
            #self.cmd("ip netns exec %s ifconfig" %(ns))
            cmd = "ip netns exec %s ls -l /sys/class/net/ | egrep 'virtual' | awk '{print $9}'" %(ns)
            vnics = self.cmd(cmd, log_level = 4).split()
            #self.log("vnics: %s" %(vnics))
            for n in vnics:
                if n != "lo":
                    self.cmd("ovs-vsctl del-port %s %s" %(bridge_name, n))
            self.cmd("ip netns del %s" %(ns))

    def ovs_start_vm (self, vm):
        '''
        '''
        name = vm.pop("name", "NoName")
        nices = vm.pop("nices", [])
        vm_type = vm.pop("type", "kvm")
        host = vm.pop("host", None)
        if vm_type == "kvm":
            return self.ovs_start_kvm_vm(name, *nices, **vm)
        elif vm_type == "container":
            image = vm.pop("image", None)
            return self.ovs_start_container("br-int", image, name, **nices)
        elif vm_type == "netns":
            return self.ovs_start_netns_vm("br-int", name, nices[0])

    def _ovs_get_container_port (self, name, **kwargs):
        '''
        Get a self-port which connect to the kwargs["name"]
        '''

        bridges = self.cmd("ovs-vsctl list-br", log_level=4)
        for b in StringIO(bridges).readlines():
            ports = self.cmd("ovs-vsctl list-ports %s" %(b.strip()), log_level=4)
            for p in StringIO(ports).readlines():
                i = self.get_interface(p.strip())
                if (name in i.get("external_ids", None)):
                    return i.get("name", None)
        return None


if __name__ == '__main__':
    '''
    #topology：
        (vr1)vrl1 -- vsl1(dvs1)vsl1 -- vrl1(vr1)
    '''

    vm1 = OvsHost("ssh://root:sangfor@172.93.63.111", name = "vm1",
            log_color = "red", log_level = options.log_level)
    vm1_br_int = {"name": "br-int", "datapath_type": "netdev",
            "port": [ {"name": "vxlan0", "type": "vxlan",
                "options:remote_ip": "192.168.63.113", "options:key": "flow" }]}
    vm1_br_phy = {"name": "br-phy", "datapath_type": "netdev",
            "other_config:hwaddr": "fe:fc:fe:b1:1d:0b",
            }
    vm1_eth1 = {"name": "eth1", "type": "phy", "ip": "192.168.63.111/16"}
    con = []
    for i in range(4):
        con.append({"name": "con%d"%(i), "type": "container", "interface": "eth1",
            "ip": "10.208.1.%d/24" %(10+i)})
    vm1.log("container: %s\n" %(json.dumps(con, indent=4)))
    vm1.cmd('ovs-vsctl show')

    vm1.ovs_connect(vm1_br_int, con[0], con[1])
    vm1.ovs_connect(vm1_br_phy, vm1_eth1)
    vm1.cmd('ovs-vsctl show')

