from collections import namedtuple
import glob
import jinja2
import os
import re
import requests
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from . import config
from .logger import logger

DEFAULT_CONFIG_PATHS = {
    'BOOTS_ROOT': '/boots',
    'TFTP_DIR': '/boots/tftp',
    'PXELINUX_CONFIG_DIR': '/boots/tftp/pxelinux.cfg',
}

SYSLINUX_URL = 'https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/syslinux-6.03.tar.gz'
BASE_DIR = os.path.dirname(__file__)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(BASE_DIR, 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True)
Host = namedtuple('Host', ['mac_addr', 'ip_addr', 'hostname'])


def render_template(tmpl_name, **options):
    return JINJA_ENVIRONMENT.get_template(tmpl_name).render(**options)


def split_mac_addr(s):
    """Return an array of bytes for the mac address in string s. This
    method is flexible in its input."""
    s = s.lower()
    m = re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
                 s)
    if not m:
        raise ValueError(f"{s} is not a valid mac address")
    delim = m.groups()[0]
    if delim:
        return s.split(delim)
    else:
        return [s[i:i+2] for i in range(0, len(s), 2)]


def create_if_not_exists(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as _:
            pass


def parse_dhcp_hosts(s):
    hosts = []
    for host_desc in s.splitlines():
        host_desc = host_desc.strip()
        if not len(host_desc) or host_desc.startswith("#"):
            continue
        m = re.match(
            r'^(?P<mac>[^,]+),(?P<ip>[^,]+),set:(?P<hostname>.+)$',
            host_desc)
        if not m:
            raise RuntimeError("Malformed DHCP hosts file")
        hosts.append(Host(*m.groups()))
    return hosts


def provision_network_boot_service(default_kernel_path,
                                   default_initrd_path,
                                   default_kernel_cmdline,
                                   config_paths):  # pragma: nocover
    os.makedirs(config_paths['TFTP_DIR'], exist_ok=True)
    if not (os.path.exists(os.path.join(config_paths['TFTP_DIR'], 'lpxelinux.0')) or
            os.path.exists(os.path.join(config_paths['TFTP_DIR'], 'ldlinux.c32'))):
        r = requests.get(SYSLINUX_URL, stream=True)
        with (tempfile.NamedTemporaryFile() as tf,
              tempfile.TemporaryDirectory() as td):
            logger.info("Downloading PXELINUX files...")
            for chunk in r.iter_content(chunk_size=16*1024):
                tf.write(chunk)
            subprocess.check_call(["tar", "xzf",
                                   tf.name, "-C", td])
            for f in [
                    'syslinux-6.03/bios/core/lpxelinux.0',
                    'syslinux-6.03/bios/com32/elflink/ldlinux/ldlinux.c32',
                    'syslinux-6.03/efi64/efi/syslinux.efi',
                    'syslinux-6.03/efi64/com32/elflink/ldlinux/ldlinux.e64']:
                shutil.move(os.path.join(td, f),
                            os.path.join(config_paths['TFTP_DIR'],
                                         os.path.basename(f)))
    os.makedirs(config_paths['PXELINUX_CONFIG_DIR'], exist_ok=True)
    default_pxelinux_config = os.path.join(config_paths['PXELINUX_CONFIG_DIR'], 'default')
    if not os.path.isfile(default_pxelinux_config):
        with open(default_pxelinux_config, 'w') as f:
            f.write(f"""DEFAULT def
label def
KERNEL {default_kernel_path}
INITRD {default_initrd_path}
APPEND {default_kernel_cmdline}
""")


class Dnsmasq():
    def __init__(self,
                 private_interface: str,
                 config_paths):
        if not shutil.which('dnsmasq'):
            raise RuntimeError("No dnsmasq found on the system!")

        self.config_paths = config_paths
        self.pid_file = os.path.join(config_paths['BOOTS_ROOT'], 'dnsmasq.pid')
        self.leases_file = os.path.join(config_paths['BOOTS_ROOT'], 'dnsmasq.leases')

        self.options_file = os.path.join(config_paths['BOOTS_ROOT'], 'options.dhcp')
        self.hosts_file = os.path.join(config_paths['BOOTS_ROOT'], 'hosts.dhcp')

        if not os.path.isfile(self.options_file):
            with open(self.options_file, 'w') as f:
                f.write("""
# Not tested, but interesting hook point for future DHCP options
option:ntp-server,10.42.0.1
""")
        create_if_not_exists(self.hosts_file)

        if not config.BOOTS_DISABLE_DNSMASQ:
            self.dnsmasq = subprocess.Popen(
                [
                    'dnsmasq',
                    '--port=0',
                    f'--pid-file={self.pid_file}',
                    f'--dhcp-hostsfile={self.hosts_file}',
                    f'--dhcp-optsfile={self.options_file}',
                    f'--dhcp-leasefile={self.leases_file}',
                    '--dhcp-match=set:efi-x86_64,option:client-arch,7',
                    '--dhcp-boot=tag:efi-x86_64,syslinux.efi',
                    '--dhcp-boot=lpxelinux.0',
                    '--dhcp-range=10.42.0.10,10.42.0.100',
                    '--dhcp-script=/bin/echo',
                    # f'--dhcp-hostsfile={static_hosts_file}',
                    f'--enable-tftp={private_interface}',
                    f'--tftp-root={config_paths["BOOTS_ROOT"]}/tftp',
                    # TODO: Rotation
                    f'--log-facility={config_paths["BOOTS_ROOT"]}/dnsmasq.log',
                    '--log-queries=extra',
                    '--conf-file=/dev/null',
                    f'--interface={private_interface}'
                ],
                bufsize=0,
            )

            # We don't want to return in a not-ready state.
            self._wait_for_dnsmasq_to_fork()

    def _wait_for_dnsmasq_to_fork(self):  # pragma: nocover
        did_fork = False
        for _ in range(10):
            logger.debug("Waiting for dnsmasq to fork...")
            if os.path.exists(self.pid_file):
                with open(self.pid_file) as f:
                    pid = f.read().strip()
                    if os.path.isfile(f'/proc/{pid}/status'):
                        did_fork = True
                        break
            time.sleep(0.2)
        if did_fork:
            logger.debug("dnsmasq is ready")
        else:
            logger.error("dnsmasq did not start in time")
            sys.exit(1)

    def _pid(self):  # pragma: nocover
        with open(self.pid_file) as pidfile:
            return int(pidfile.read())

    def reload(self):  # pragma: nocover
        if not config.BOOTS_DISABLE_DNSMASQ:
            os.kill(self._pid(), signal.SIGHUP)

    def stop(self):  # pragma: nocover
        if not config.BOOTS_DISABLE_DNSMASQ:
            os.kill(self._pid(), signal.SIGKILL)
            os.remove(self.pid_file)

    def add_static_address(self, mac_addr, ip_addr, hostname):
        mac_addr = ':'.join(split_mac_addr(mac_addr))

        logger.info("%s. ip=%s hostname=%s",
                    mac_addr, ip_addr, hostname)

        with open(self.hosts_file, 'r') as f:
            machines = parse_dhcp_hosts(f.read())
            new_machines = [m for m in machines if m.mac_addr != mac_addr]
            new_machines.append(Host(mac_addr, ip_addr, hostname))
            config = render_template(
                'dnsmasq-dhcp-host.jinja',
                machines=sorted(new_machines, key=lambda m: m[0]))
        try:
            # Make an effort to avoid dnsmasq seeing a partial write.
            with tempfile.NamedTemporaryFile(mode='w',
                                             dir=self.config_paths['PXELINUX_CONFIG_DIR'],
                                             delete=False) as tf:
                tf.write(config)
                tf.flush()
                os.rename(tf.name, self.hosts_file)
                # Ensure the dnsmasq nobody can read us
                os.chmod(self.hosts_file, 0o644)
        finally:
            self.reload()


class BootService():
    def __init__(self,
                 private_interface=None,
                 default_kernel=None,
                 default_initrd=None,
                 default_cmdline=None,
                 config_paths=DEFAULT_CONFIG_PATHS):
        self.private_interface = private_interface or config.PRIVATE_INTERFACE
        self.default_kernel = default_kernel or config.BOOTS_DEFAULT_KERNEL
        self.default_initrd = default_initrd or config.BOOTS_DEFAULT_INITRD
        self.default_cmdline = default_cmdline or config.BOOTS_DEFAULT_CMDLINE
        self.config_paths = config_paths

        # Ensure these steps happen on the calling thread, not
        provision_network_boot_service(
            self.default_kernel,
            self.default_initrd,
            self.default_cmdline,
            config_paths)

        self.dnsmasq = Dnsmasq(self.private_interface, config_paths)

    def stop(self):
        self.dnsmasq.stop()
        for config_file in glob.glob(os.path.join(self.config_paths['PXELINUX_CONFIG_DIR'], '01-*')):
            os.remove(config_file)

    def write_network_config(self, mac_address, ip_address, hostname):
        # Are static mappings that useful here? We're basically
        # enforcing the initial DHCP offer, but it does allow a
        # specific address to be set at least.
        logger.debug("%s: ip=%s hostname=%s",
                     mac_address, ip_address, hostname)
        self.dnsmasq.add_static_address(mac_address, ip_address, hostname)

    def encode_pxelinux_filename(self, mac_addr):
        if isinstance(mac_addr, str):
            mac_addr = split_mac_addr(mac_addr)
        assert isinstance(mac_addr, list) and \
            len(mac_addr) == 6
        return "01-" + '-'.join(mac_addr)

    def pxelinux_filename_from_mac(self, mac_addr):
        if mac_addr == "default":
            filename = "default"
        else:
            filename = self.encode_pxelinux_filename(mac_addr)

        return os.path.join(self.config_paths['PXELINUX_CONFIG_DIR'],
                            filename)

    def write_pxelinux_config(self,
                              mac_addr,
                              kernel_path=None,
                              cmdline=None,
                              initrd_path=None):
        pxelinux_filename = self.pxelinux_filename_from_mac(mac_addr)
        logger.info("%s. kernel=%s, cmdline=%s, initrd=%s",
                    pxelinux_filename, kernel_path, cmdline, initrd_path)
        result = (render_template(
            'pxelinux-raw.jinja',
            kernel_path=kernel_path or self.default_kernel,
            cmdline=cmdline or self.default_cmdline,
            initrd_path=initrd_path or self.default_initrd))

        with open(pxelinux_filename, 'w') as config:
            config.write(result)

    def remove_pxelinux_config(self, mac_addr):
        pxelinux_filename = self.pxelinux_filename_from_mac(mac_addr)
        if os.path.exists(pxelinux_filename):
            logger.info("%s", pxelinux_filename)
            os.remove(pxelinux_filename)


if __name__ == '__main__':  # pragma: nocover
    if len(sys.argv) == 2:
        private_interface = sys.argv[1]
    else:
        private_interface = config.PRIVATE_INTERFACE
    try:
        boots = BootService(private_interface=private_interface, config_paths=DEFAULT_CONFIG_PATHS)
        boots.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        boots.stop()
