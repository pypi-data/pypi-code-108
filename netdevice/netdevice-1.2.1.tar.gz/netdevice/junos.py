#!/usr/bin/env python3

from netdevice import linux
import simplejson as json
import pexpect
import xmltodict
import ipaddress
import random
from lxml import etree
try:
    # Python 2.
    from StringIO import StringIO
    # Python 3.
except ImportError:
    from io import StringIO
import sys, os, time
import collections
import tempfile

class JunosDevice(linux.LinuxDevice):
    '''
    A base class for common Juniper Junos devices.
    '''
    def __init__ (self, server = None, **kwargs):

        if "log_color" not in kwargs.keys():
            rn = random.randint(0, 2)
            kwargs["log_color"] = rn == 1 and "blue" or "light_blue"

        kwargs["type"] = 'Junos'
        self.configure_mode = False
        linux.LinuxDevice.__init__(self, server, **kwargs)
        if not self.configure_mode:
            self.configure_mode = True
            self._enter_configure_mode()
        self._get_spus(with_log = False)
        self._preconfig()
        self.log("%s = %s\n" %(self.name, json.dumps(self.attributes, indent=4)))

    def __del__ (self):
        '''
        Recycle resource when the object is destroied.
        '''
        #postconfig
        if self['postconfig']:
            for c in self['postconfig']:
                self.configure(c)
            self.configure("commit")
        self.log("%s.%s(%s), finish in %.2f seconds\n" %(self.__class__.__name__,
            sys._getframe().f_code.co_name,
            self.version,
            time.time() - self.start_time))
        #linux.LinuxDevice.__del__(self)

    def cmd (self, cmd, mode = "shell", timeout = 30, **kwargs):
        '''
        There are total 4 modes for junos devices:

            1) shell: execute the command in shell mode and return the result,
                this is the default mode and it looks like linux.cmd().

            2) cli: execute the command in cli mode and return the result,
                self.cmd(cmd, mode = "cli") equal to self.cli(cmd), see detail
                in seld.cli()

            3) configure: execute the command in configure mode and return the
                result, self.cmd(cmd, mode = "configure") equal to
                self.configure(cmd), see detail in seld.configure()

            4) vty: execute the command in vty mode and return the result,
                self.cmd(cmd, mode = "vty") equal to self.vty(cmd), see detail
                in seld.vty()

        Supported options include:

            timeout: time to wait for the execute command return. default is 5
                     seconds

        '''
        if mode == "shell":
            # shell/vty command use different prompt from configure
            linux.LinuxDevice.cmd(self, "run start shell csh", 
                    expect = self.original_prompt, timeout = 3, with_log = False)
            prompt = "\[NETDEVICE\][\$\#] "
            linux.LinuxDevice.cmd(self, self.PROMPT_SET_CSH, expect = prompt,
                    timeout=1, with_log = False)
            output = linux.LinuxDevice.cmd(self, cmd, expect = prompt,
                    timeout = timeout, **kwargs)
            linux.LinuxDevice.cmd(self, "exit", with_log = False)
            #self.log("%s\n" %(output), leading = "    ", level = linux.LOG_INFO)
            return output
        elif mode == "cli":
            return self.cli(cmd, **kwargs)
        elif mode == "configure":
            return self.configure(cmd, **kwargs)
        elif mode == "vty":
            return self.vty(cmd, **kwargs)

        return None

    def cli (self, *args, **kwargs):
        '''
        Execute a list of cli command and return the execution result of the
        last command.

        @parse: Normally, the result will be plain text or xml text. But if
        the @parse is given, the result will be parsed and a list of
        dictionary for @parse will be returned. It's useful to parse the xml
        result. For example the following command return a list of session in
        dictionary::
        
            sessions = dut.cli('show security flow session',
                               parse = "flow-session")
            print sessions[0]['session-identifier']

        Whild the following command will return the plain text result::

            output = dut.cli('show security flow session')
            print output
        '''

        commands = []
        for cmd in args:
            cmd = filter(lambda x: x.strip()[0] != '#', StringIO(cmd).readlines())
            commands += map(lambda x: 'run ' + x.strip(), cmd)
        return self.configure(*commands, **kwargs)

    def configure (self, *args, **kwargs):
        '''
        Execute a configure command and return the result of the last command.
        Sematics is like self.cli, see detail in self.cli()
        '''
         
        commands = []
        for cmd in args:
            #print StringIO(cmd.strip()).readlines()
            cmd = filter(lambda x: (x.strip()) and (x.strip()[0] != '#'),
                    StringIO(cmd.strip()).readlines())
            # remove the leading or trailing \r\n
            commands += map(lambda x: x.strip(), cmd)
        #print commands
        if not commands:
            return None

        #suffix = ' | display xml | no-more' if kwargs.get("parse", None) else ' | no-more'
        suffix1 = ' | display xml' if kwargs.get("parse", None) else ''
        for c in commands:
            suffix2 = ' | no-more' if ("show" in c) else ''

            if "commit" in c:
                #t = self.thread(target=self.sleep,
                #        args=(kwargs.get('timeout', 120), 50, '>', "commit"))
                self.log("Wait for at most %d seconds to commit."
                        %(kwargs.get('timeout', 120)))

            output = linux.LinuxDevice.cmd(self, c + suffix1 + suffix2, **kwargs)
            #if "commit" in c:
            #    # Wait the commit finish in case of HA.
            #    self.terminate_loop = True
            #    #linux.LinuxDevice.cmd(self,
            #    #        "show | compare rollback 1 | no-more", **kwargs)

            if kwargs.get('parse', None):
                #self["log_level"] = self["log_level"] + 1
                result = []
                elements = etree.HTML(output).xpath("//%s" %(kwargs['parse']))
                for e in elements:
                    #print etree.tostring(e)
                    res = xmltodict.parse(etree.tostring(e,  with_tail=False))
                    result.append(res['%s' %(kwargs['parse'])])
                #self.log(json.dumps(result, indent=4))

        return result if kwargs.get("parse", None) else output

    def vty (self, *args, **kwargs):
        '''
        equal cmd(..., mode = "vty")

        Execute every line in every argument on every SPU(if not given) and
        return the result.

        Supported options include:

            timeout: time to wait for the execute command return. default is 5
                     seconds
            tnp_addr: tnp address to execute, if not execut the command on
                      every SPU.
        '''
        spus = kwargs.get("tnp_addr", None) and kwargs["tnp_addr"] or self["spus"]
        if type(spus)!=list:
            spus = [spus]

        linux.LinuxDevice.cmd(self, "run start shell csh",
                expect = self.original_prompt, timeout = 3, with_log = False)
        prompt = self.prompt
        self.prompt = "\[NETDEVICE\][\$\#] "
        linux.LinuxDevice.cmd(self, self.PROMPT_SET_CSH, timeout=1,
                with_log = False, log_level = self.LOG_DEBUG)

        cprod = "cprod"
        if kwargs.get("output", None):
            cprod += " -o %s" %(kwargs["output"])
        if kwargs.get("timeout", None):
            cprod += " -w %s" %(kwargs["timeout"])

        #cprod = "cprod -o %s" %(kwargs["output"]) if kwargs.get("output", None) else "cprod"
        with tempfile.SpooledTemporaryFile(mode='w',) as temp:
            temp.writelines(map(lambda x: (x + '\n'), args))
            temp.seek(0)
            lines = temp.readlines()
            if len(lines) == 1:
                commands = '-c "%s"' %(lines[0].strip())
            else:
                # Multiple commands, use a temp file
                linux.LinuxDevice.cmd(self, "rm -rf ~/tmpa.sh")
                for c in lines:
                    #print c.strip()
                    linux.LinuxDevice.cmd(self,
                            'echo "%s" >> ~/tmpa.sh' %(c.strip()),
                            **kwargs)
                commands = '~/tmpa.sh'

        output = ""
        for spu in spus:
            output += linux.LinuxDevice.cmd(self,
                    '%s -A "%s" %s' %(cprod, spu, commands),
                    **kwargs)

        if len(lines) > 1:
            linux.LinuxDevice.cmd(self, "rm -rf ~/tmpa.sh;")

        # Restore the original prompt
        self.prompt = prompt
        linux.LinuxDevice.cmd(self, "exit", with_log = False)
        return output

    #def vty (self, *args, **kwargs):
    #    '''
    #    equal cmd(..., mode = "vty")

    #    Execute every line in every argument on every SPU(if not given) and
    #    return the result.

    #    Supported options include:

    #        timeout: time to wait for the execute command return. default is 5
    #                 seconds
    #        tnp_addr: tnp address to execute, if not execut the command on
    #                  every SPU.
    #    '''
    #    spus = kwargs.get("tnp_addr", False) and [kwargs["tnp_addr"]] or self["spus"]

    #    linux.LinuxDevice.cmd(self, "run start shell csh",
    #            expect = self.original_prompt, timeout = 3, with_log = False)
    #    output = ""
    #    for spu in spus:
    #        linux.LinuxDevice.cmd(self, "vty %s" %(spu),
    #                expect = "vty\)# ", timeout = 5, with_log = False)
    #        for cmd in args:
    #            with StringIO(cmd) as f:
    #                for line in f.readlines():
    #                    output += linux.LinuxDevice.cmd(self, line.strip(),
    #                            expect = ["vty\)# ", "---(more)---"],
    #                            command_leading = "%s(vty)# "%(spu), **kwargs)
    #        linux.LinuxDevice.cmd(self, "quit",
    #                expect = self.original_prompt, timeout = 3, with_log = False)

    #    # return to the configure mode.
    #    linux.LinuxDevice.cmd(self, "exit", with_log = False)
    #    return output

    def reboot (self):
        '''
        reboot the device and reconnect to it until it bootup.
        '''
        self.cli("request system reboot", expect = "Reboot the system \? \[yes,no\] \(no\)")
        self.configure("yes")

        # reconnect to the object after reboot
        del self.psession
        self.sleep(60)
        while True:
            try:
                self.prompt = "\[NETDEVICE\][\$\#] "
                self.psession = self.login()
            except Exception as e:
                print(e)
                self.sleep(60)
            else:
                self.connected = True
                #self.del__configure_interface()
                #self._preconfig()
                self._enter_configure_mode()
                break
        self.log('succeed to re-connect the device.\n')

        # wait for all spu are up
        while not self.is_system_up():
            self.sleep(60)
        self.log("system is up.\n")

    def install_image (self, local = None, remote = None, **kwargs):
        '''
        Install a image and reboot the dut, wait until it is up with all
        SPU/SPC.
        
        @local: install a local image, first upload the image to /var/tmp/ on
        the DUT and then install it.

        @remote: install a image on the DUT
        '''

        # transfer the image.
        if local:
            if not os.path.exists(local):
                self.log("%s not exist" %(local), level = linux.LOG_ERR)
                raise Exception("%s not exist" %(local))
            self.put_file(local, '/var/tmp/')
            image = '/var/tmp/%s' %(os.path.basename(local))
        elif remote:
            image = remote
        else:
            self.log("No image provide", level = linux.LOG_ERR)
            return

        # Install the image with the verbose log
        #self.log("install the image: %s\n" %(image))
        #if not self['debug']:
        #    self.psession.logfile = sys.stdout
        self.configure("run request system software add %s no-copy no-validate" %(image),
                timeout = 600)
        #if not self['debug']:
        #    self.psession.logfile = None
        if kwargs.get("reboot", True):
            self.cli("request system reboot", expect = "Reboot the system \? \[yes,no\] \(no\)")
            self.configure("yes")

        # reconnect to the object after reboot
        del self.psession
        self.log("sleep 600 seconds to wait for %s to reboot\n" %(self["name"]))
        linux.sleep_with_bar(600)
        while True:
            try:
                self.psession = self.login()
            except Exception as e:
                print('Wait for 20 more seconds')
                linux.sleep_with_bar(20)
            else:
                self._enter_configure_mode()
                break
        self.log('succeed to re-connect the device.\n')

        # wait for all spu are up
        while not self.is_system_up():
            linux.sleep_with_bar(60)
        self.log("system is up.\n")

    def is_system_up (self):
        '''
        check all the pic to see if the system bootup.
        '''
        pics = self.cli('show chassis fpc pic-status', parse = 'pic',
                log_level = self.LOG_DEBUG)
        if not pics:
            self.log("there is no fpc loaded")
            return False
        for pic in pics:
            if pic.get('pic-state', "unknown") != "Online":
                self.log("pic not online:\n  PIC %s  %s       %s\n" %(pic['pic-slot'],
                    pic['pic-state'], pic.get('pic-type', "")))
                return False
        return True

    #def dumps(self):
    #    '''
    #    dump the attributes.
    #    '''
    #    linux.LinuxDevice.dumps(self)
    #    self.log('"model": %s' %(self.model))
    #    self.log('"junos_version": %s' %(self.junos_version))
    #    self.log('"isha": %s' %(self.isha))

    def _get_spus (self, **kwargs):
        '''
        Get the spu list of the srx.
        '''

        version = self.cli("show version", parse = "software-information",
                with_log = False)
        self.model = version and version[0]["product-model"] or "Unknown"
        #self.junos_version = version and version[0]["junos-version"] or "Unknown"
        cluster = self.cli("show chassis cluster status",
                parse = "redundancy-group", with_log = False)
        self.isha = cluster and True or False

        if self.model.lower() in ["srx320", "srx550m", "vsrx", "srx345"]:
            spus = self.isha and ["node0.fwdd", "node1.fwdd"] or ["fwdd"]
        elif self.model.lower() in ["srx1500", "srx4100", "srx4200", "srx4600", "vsrx"]:
            spus = self.isha and ["node0.fpc0", "node1.fpc0"] or ["fpc0"]
        else:
            # List all the SPUs' TNPaddr on high end:
            spus = []
            results = self.cmd('tnpdump', with_log = False)
            f = StringIO(results)
            for i in f.readlines():
                if ".pic" in i:
                    tmp = i.split()
                    spus.append(tmp[0])
            f.close()
        self["product-model"] = version[0]["product-model"]
        self["spus"] = spus
        self["junos-version"] = version[0]["junos-version"]
        return spus

    def _enter_configure_mode (self, timeout = 60):
        self.log("%s.%s()" %(self.__class__.__name__, sys._getframe().f_code.co_name),
                level = linux.LOG_DEBUG)

        # Junos is always in configure mode, 
        if self.name:
            self.prompt = "%s@%s[\$\#\>] " %(self["username"], self.name)
        else:
            self.prompt = "%s[\$\#\>] " %(self["username"])
        linux.LinuxDevice.cmd(self, "cli", timeout = timeout, with_log = False)

        if self.name:
            self.prompt = r"\[edit\]\r\n%s@%s#" %(self["username"], self.name)
        else:
            self.prompt = r"\[edit\]\r\n%s#" %(self["username"])
        linux.LinuxDevice.cmd(self, "configure", timeout = timeout,
                with_log = False)

    def _preconfig(self):
        '''
        Override LinuxDevice._preconfig()
        '''
        # enter configure mode at first

        if self["preconfig"]:
            if not self.configure_mode:
                self.configure_mode = True
                self._enter_configure_mode()

            if isinstance(self["preconfig"], list):
                for c in self["preconfig"]:
                    self.configure(c)
            elif isinstance(self["preconfig"], str):
                f = StringIO(self["preconfig"])
                for c in f.readlines():
                    self.configure(c.strip())
                f.close()
            self.configure("commit")

    def _print_a_session (self, session):
        #print(session)
        out = "Session ID: %s, Policy name: %s, Timeout: %s, %s" %(session['session-identifier'],
                session['policy'], session['timeout'], session['sess-state'])

        #print(session)
        if session.get("session-state"):
            out += ", state: %s" %(session.get("session-state"))
        if session.get("session-flag"):
            out += ", flags: %s" %(session.get("session-flag"))
        if session.get("session-state") or session.get("session-flag"):
            out += "\r\n"

        if "resource-manager-information" in session:
            rm = session["resource-manager-information"]
            out += "Resource information : %s, %s, %s\r\n" %(rm["client-name"],
                    rm["group-identifier"], rm["resource-identifier"])
        for f in session['flow-information']:
            out += "  %s: %s/%s --> %s/%s;%s, Conn tag: %s, If: %s, Pkts: %s, Bytes: %s\r\n" \
                    %(f['direction'], f['source-address'], f['source-port'],
                    f['destination-address'], f['destination-port'],
                    f['protocol'], f.get('conn-tag', 0),
                    f['interface-name'], f['pkt-cnt'],
                    f['byte-cnt'])
        self.log(out)

    def x_get_interface (self, name = None):
        '''
        Get interface configuration given a interface name.
        '''

        if not self.configure_mode:
            self.configure_mode = True
            self._enter_configure_mode()

        #results = self.cli("show interfaces %s brief" %(name), parse = "logical-interface", log_level = 10)
        results = self.cli("show interfaces terse zone",
                parse = "logical-interface", with_log = False)
        for i in results:
            #print(i["name"], i)
            name = i["name"]
            self.interface[name] = collections.OrderedDict()
            self.interface[name]["name"] = name
            self.interface[name]["zone"] = i["zonename"]

            if i.get("address-family", None):
                address_family = isinstance(i["address-family"], list) and i["address-family"] or [i["address-family"]]
                for family in address_family:
                    if not family.get("interface-address", None):
                        continue
                    address = family["interface-address"]
                    address = isinstance(address, list) and address[0]["ifa-local"] or address["ifa-local"]
                    address = isinstance(address, dict) and address["#text"] or address
                    #print(family["address-family-name"], address)
                    self.interface[name][family["address-family-name"]] = address
        return

    def x_get_interfaces3 (self, name):
        '''
        Get interface configuration given a interface name.
        '''

        if not self.configure_mode:
            self.configure_mode = True
            self._enter_configure_mode()

        results = self.cli("show interfaces %s brief" %(name),
                parse = "logical-interface", log_level = 10)
        logical_interface = results[0]
        #print(json.dumps(logical_interface, indent=4))
        interface = collections.OrderedDict()
        interface["name"] = logical_interface["name"]
        interface["zone"] = logical_interface.get("logical-interface-zone-name", None)

        address_family = logical_interface.get("address-family", None)
        if not isinstance(address_family, list):
            address_family = [address_family]

        #print(address_family)
        for family in address_family:
            family_name = family["address-family-name"]
            interface[family_name] = []
            address = family.get("interface-address", None)
            if address is None:
                continue
            elif not isinstance(address, list):
                address = [address]

            for addr in address:
                ipaddr = isinstance(addr["ifa-local"], dict) and addr["ifa-local"]["#text"] or addr["ifa-local"]
                #if family_name == "inet" or family_name == "inet6":
                #    ipaddr = ipaddress.ip_interface(ipaddr)
                #interface[family_name].append(ipaddr)
                interface[family_name].append(ipaddress.ip_interface(unicode(ipaddr)))
        return interface

    def x_set_interface (self, *args, **kwargs):
        """
        Re-configure the interface with the given parameters.

        From release1.0.6, we will only configure the interfaces themselves,
        won't configure the zone and other things.

        call examples:
            int0 = {"name": "xe-1/0/0",
                    "inet": "41.0.0.111/24",
                    "inet6": "2001::111/64",
                    "zone": "trust" }
            dut.x_set_interface(int0)
        """
        #print("%s.%s invoked" %(self.__class__.__name__, sys._getframe().f_code.co_name))
        for arg in args:
            if not "name" in arg.keys():
                continue
            name = arg['name'].split('.')
            self.configure("delete interfaces %s unit %s" %(name[0], name[1]), **kwargs)
            if "inet" in arg.keys():
                self.configure("set interfaces %s unit %s family inet address %s" %(name[0], name[1], arg["inet"]), **kwargs)
            if "inet6" in arg.keys():
                self.configure("set security forwarding-options family inet6 mode flow-based", **kwargs)
                self.configure("set interfaces %s unit %s family inet6 address %s" %(name[0], name[1], arg["inet6"]), **kwargs)
        #self.configure("commit", **kwargs)

    def x_set_zone (self, zone = None, interfaces = None,
            services = "all", protocols = "all"):
        """
        Delete the @zone and re-configure it with the new parameters.

        call examples:
            dut.x_set_zone("trust", "xe-9/0/2.0", "all", "all")
            dut.x_set_zone("untrust", ["reth1.0", "reth3.0"], "all", "all")
        """
        #print("%s.%s invoked" %(self.__class__.__name__, sys._getframe().f_code.co_name))
        if (not zone) or (not services):
            self.log("Please provide the zone and interfaces.")
            return

        self.configure("delete security zones security-zone %s" %(zone))
        common_part = "set security zones security-zone %s " %(zone)
        if isinstance(services, list):
            for s in services:
                self.configure(common_part + "host-inbound-traffic system-services " + s)
        else:
            self.configure(common_part + "host-inbound-traffic system-services " + services)

        if isinstance(protocols, list):
            for p in protocols:
                self.configure(common_part + "host-inbound-traffic protocols " + p)
        else:
            self.configure(common_part + "host-inbound-traffic protocols " + protocols)

        if isinstance(interfaces, list):
            for i in interfaces:
                self.configure(common_part +  "interfaces %s" %(i))
        else:
            self.configure(common_part +  "interfaces %s" %(interfaces))
        #self.configure("commit", **kwargs)

    def x_set_policy (self,
            from_zone = "trust", to_zone = "untrust", name = "t2u",
            source_address = "any", destination_address = "any",
            application = "any", dynamic_application = None, 
            action = "permit", **kwargs):
        """
        Re-configure the policy with the given parameters.

        call examples:
        self.dut.x_set_policy("trust", "untrust", "t2u111", "any", "any", "any",
                              action = ["permit", "services-offload"])

        """
        #print("%s.%s invoked" %(self.__class__.__name__, sys._getframe().f_code.co_name))

        # Remove all the policies in the same zone to make sure the new one is active.
        self.configure("delete security policies from-zone %s to-zone %s"
                %(from_zone, to_zone))
        common_part = "set security policies from-zone %s to-zone %s policy %s "\
                %(from_zone, to_zone, name)

        # source-address
        if isinstance(source_address, list):
            for s in source_address:
                self.configure(common_part +  "match source-address %s" %(s))
        else:
            self.configure(common_part +  "match source-address %s" %(source_address))

        # destination-address
        if isinstance(destination_address, list):
            for d in destination_address:
                self.configure(common_part +  "match destination-address %s" %(d))
        else:
            self.configure(common_part +  "match destination-address %s" %(destination_address))

        # application
        if isinstance(application, list):
            for app in application:
                self.configure(common_part +  "match application %s" %(app))
        else:
            self.configure(common_part +  "match application %s" %(application))

        # dynamic-application
        if isinstance(dynamic_application, list):
            for dynapp in dynamic_application:
                self.configure(common_part +  "match dynamic-application %s" %(dynapp))
        elif dynamic_application:
            self.configure(common_part +  "match dynamic-application %s" %(dynamic_application))

        # action
        action_line = common_part + "then "
        for a in action:
            action_line += "%s " %(a)
        self.configure(action_line)

        #self.configure("commit", **kwargs)


    def x_print_session (self, sessions):
        '''
        Convert a or lists of session in dictionary to plain text.
        '''
        if type(sessions)==list:
            for session in sessions:
                self._print_a_session(session)
            self.log("Total sessions: %d\n" %(len(sessions)))
        else:
            self._print_a_session(sessions)

    def x_configure_trace (self, *args, **kwargs):
        '''
        configure trace file, For examples:

            dut.x_configure_trace("flow", "alg dns", "dynamic-application",
                                  filename = "flow.log", size = "50m")

        '''

        lines = '''
        delete security flow traceoptions
        set security traceoptions flag all
        set security traceoptions level verbose
        '''
        lines += "set security traceoptions file %s\n" %(kwargs.get('filename', "flow.log"))
        lines += "set security traceoptions file size %s\n" %(kwargs.get('size', "100m"))

        for arg in args:
            lines += "set security %s traceoptions flag all\n" %(arg)
            if "alg" in arg:
                # To print the trace in the same file with flow
                self.vty("set jsf trace per-plugin-trace disable")
        lines += "commit"

        #if kwargs.get('vty', False):
        #    self.vty_trace = True
        #if kwargs.get('syslog', False):
        #    self.syslog_trace = True
        self.configure(lines)

    def x_configure_vty_trace (self, *args, **kwargs):
        '''
        configure trace file
        
        An examples, to enable flow/policy/dynamic-application traceoption and
        write the trace into one file:

            dut.x_configure_vty_trace("flow", "policy", "fwdd")

        '''
        #debug usp flow pkt-trace enable
        flow_debug_config = """
            debug usp flow enable
            debug usp flow pkt-trace enable
            set usp flow local-debug-buf size 10240
            set usp flow local-debug-buf state 1
            clear usp flow trace
            """
        policy_debug_config = '''
            debug usp policy application error
            debug usp policy config error
            debug usp policy context error
            debug usp policy entity error
            debug usp policy general error
            debug usp policy ipc error
            debug usp policy tlv error
            debug usp policy jtree error
            debug usp policy lookup error
            debug usp policy prefix error
            debug usp policy state error
            '''
        dynapp_debug_config = '''
            debug usp dynapp config verbose
            debug usp dynapp general verbose
            debug usp dynapp ipc verbose
            debug usp dynapp lkp verbose
            '''

        idp_debug_config = '''
            set usp flow local-debug-buf state 1
            debug usp idp level debug
            debug usp idp qmodules ids enable
            debug usp idp features all enable
            debug usp idp qmodules all enable
            debug usp idp services 0xffffffff
            debug usp idp services2 0xffffffff
            debug usp idp features memory disable
            debug usp idp features device disable
            debug usp idp features ioctl disable
            '''
        jdpi_debug_config = '''
            plugin jdpi set debug level 3
            plugin jdpi set debug module all enable
            plugin jdpi set debug module memory disable
            plugin jdpi set debug module stats disable
            plugin jdpi set debug module timer disable
            '''
        interface_debug_config = '''
            debug usp interface event
            debug usp interface extension
            debug usp interface tunnel
            '''
        appfw_debug_config = '''
            debug usp flow enable
            plugin jdpi set debug module all enable
            plugin jdpi set debug level 3
            set usp flow local-debug-buf state 1
            debug usp appfw ruleset verbose
            debug usp appfw rule verbose
            debug usp appfw lkp verbose
            '''
        fwdd_debug_config = """
            debug fwdd inq        verbose
            debug fwdd jexec-trace    verbose
            debug fwdd jtree-exec    verbose
            debug fwdd l2-fwd      verbose
            debug fwdd l2-parse     verbose
            debug fwdd l2-rewrite    verbose
            debug fwdd l3-fwd      verbose
            debug fwdd l3-parse     verbose
            debug fwdd l3-rewrite    verbose
            debug fwdd lookup      verbose
            debug fwdd notif       verbose
            debug fwdd outq       verbose
            debug fwdd packet-processing verbose
            debug fwdd result      verbose
            debug fwdd sched       verbose
            debug fwdd tag-fwd      verbose
            debug fwdd tag-parse     verbose
            debug fwdd tag-rw      verbose
            debug fwdd tag-rw      verbose
            debug fwdd inq        verbose
            debug fwdd jexec-trace    verbose
            debug fwdd jtree-exec    verbose
            debug fwdd l2-fwd      verbose
            debug fwdd l2-parse     verbose
            debug fwdd l2-rewrite    verbose
            debug fwdd l3-fwd      verbose
            debug fwdd l3-parse     verbose
            debug fwdd l3-rewrite    verbose
            debug fwdd lookup      verbose
            debug fwdd notif       verbose
            debug fwdd outq       verbose
            debug fwdd packet-processing verbose
            debug fwdd result      verbose
            debug fwdd sched       verbose
            debug fwdd tag-fwd      verbose
            debug fwdd tag-parse     verbose
            debug fwdd tag-rw      verbose
            debug fwdd tag-rw      verbose
            debug fwdd mlink-assemble verbose
            debug fwdd mlink-frag verbose
            debug fwdd cos-classify verbose
            """
            #clear usp fwdd
        commands = ''
        if "flow" in args:
            commands += flow_debug_config + '\n'
        if "policy" in args:
            commands += policy_debug_config + '\n'
        if "dynapp" in args:
            commands += dynapp_debug_config + '\n'
        if "jdpi" in args:
            commands += jdpi_debug_config + '\n'
        if "interface" in args:
            commands += interface_debug_config + '\n'
        if "appfw" in args:
            commands += appfw_debug_config + '\n'
        if "fwdd" in args:
            commands += fwdd_debug_config + '\n'
        if "idp" in args:
            commands += idp_debug_config + '\n'
        self.vty(commands)

    def x_configure_tenants (self, name, *args, **kwargs):
        '''
        configure trace file
        
        An examples, to enable flow/policy/dynamic-application traceoption and
        write the trace into one file:

            dut.x_configure_vty_trace("flow", "policy", "fwdd",
                                  filename = "flow.log", size = "50m")

        '''
        flow_debug_config = """
            debug usp flow enable
            debug usp flow pkt-trace enable
            set usp flow local-debug-buf size 10240
            set usp flow local-debug-buf state 1
            """
        policy_debug_config = '''
            debug usp policy application verbose
            debug usp policy config verbose
            debug usp policy context verbose
            debug usp policy entity verbose
            debug usp policy general verbose
            debug usp policy ipc verbose
            debug usp policy tlv verbose
            debug usp policy jtree verbose
            debug usp policy lookup verbose
            debug usp policy prefix verbose
            debug usp policy state verbose
            '''

if __name__ == '__main__':
    dut = {
            "host": "tangshan",
            "username": "dev",
            "password": "1234",
            "root_password": "5678",
            #"autoconfig":  True,
            "interfaces": [
                { "ip": "2.2.2.2/24", "ip6": "2002::2/64", "name": "fe-0/0/2.0", "zone": "untrust" },
                { "ip": "4.4.4.1/24", "ip6": "2004::1/64", "name": "fe-0/0/6.0", "zone": "trust" }],
            "preconfig": [ "set routing-options static route 1.1.1.0/24 next-hop 2.2.2.1"] 
            }
    print(dut.cli("show version"))
