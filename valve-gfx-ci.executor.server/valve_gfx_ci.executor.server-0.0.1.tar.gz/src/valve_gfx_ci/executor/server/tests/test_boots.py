from pathlib import Path
from unittest.mock import patch
from server.boots import (
    split_mac_addr,
    parse_dhcp_hosts,
    Dnsmasq,
    BootService,
)
import glob
import os
import pytest
import shutil

import server


def test_split_mac_addr():
    assert split_mac_addr('00:01:02:03:04:05') == \
        ['00', '01', '02', '03', '04', '05']
    assert split_mac_addr('00-01-02-03-04-05') == \
        ['00', '01', '02', '03', '04', '05']
    assert split_mac_addr('000102030405') == \
        ['00', '01', '02', '03', '04', '05']
    with pytest.raises(ValueError):
        # Too long
        split_mac_addr('00:01:02:03:04:05:06')
    with pytest.raises(ValueError):
        # Too short
        split_mac_addr('00:01:02:03:04')
    with pytest.raises(ValueError):
        # Bad separator
        split_mac_addr('00:01:02:03:04?05')
    with pytest.raises(ValueError):
        split_mac_addr('garbage')


def test_parse_dhcp_hosts():
    hosts = parse_dhcp_hosts("""
# A comment is fine
10:62:e5:04:39:89,10.42.0.10,set:igalia-amd-gfx8-1


10:62:e5:0e:0a:54,10.42.0.11,set:igalia-amd-gfx8-2
""")
    assert len(hosts) == 2
    assert ('10:62:e5:04:39:89', '10.42.0.10', 'igalia-amd-gfx8-1') in \
        hosts
    assert ('10:62:e5:0e:0a:54', '10.42.0.11', 'igalia-amd-gfx8-2') in \
        hosts
    hosts = parse_dhcp_hosts("")
    assert len(hosts) == 0
    with pytest.raises(RuntimeError):
        # Deleted first comma
        hosts = parse_dhcp_hosts("""
10:62:e5:04:39:8910.42.0.10,set:igalia-amd-gfx8-1
""")


@patch.object(server.boots.Dnsmasq, '_wait_for_dnsmasq_to_fork')
@patch("subprocess.Popen")
def test_dnsmasq_no_binary(popen_mock, dnsmasq_waiter, tmp_path):
    with patch.object(shutil, 'which', lambda _: False), pytest.raises(RuntimeError):
        _ = Dnsmasq('br0', {})


@patch.object(server.boots.Dnsmasq, '_wait_for_dnsmasq_to_fork')
@patch("subprocess.Popen")
def test_dnsmasq_launch(popen_mock, dnsmasq_waiter, tmp_path):
    paths = {
        'BOOTS_ROOT': tmp_path,
        'TFTP_DIR': f'{tmp_path}/tftp',
        'PXELINUX_CONFIG_DIR': f'{tmp_path}/pxelinux.cfg',
    }
    _ = Dnsmasq('br0', paths)
    dnsmasq_waiter.assert_called_once()
    popen_mock.assert_called_once_with(
        ['dnsmasq',
         '--port=0',
         f'--pid-file={tmp_path}/dnsmasq.pid',
         f'--dhcp-hostsfile={tmp_path}/hosts.dhcp',
         f'--dhcp-optsfile={tmp_path}/options.dhcp',
         f'--dhcp-leasefile={tmp_path}/dnsmasq.leases',
         '--dhcp-match=set:efi-x86_64,option:client-arch,7',
         '--dhcp-boot=tag:efi-x86_64,syslinux.efi',
         '--dhcp-boot=lpxelinux.0',
         '--dhcp-range=10.42.0.10,10.42.0.100',
         '--dhcp-script=/bin/echo',
         '--enable-tftp=br0',
         f'--tftp-root={tmp_path}/tftp',
         f'--log-facility={tmp_path}/dnsmasq.log',
         '--log-queries=extra',
         '--conf-file=/dev/null',
         '--interface=br0'], bufsize=0)


@patch.object(server.boots.Dnsmasq, 'reload')
@patch.object(server.boots.Dnsmasq, '_wait_for_dnsmasq_to_fork')
@patch("subprocess.Popen")
def test_dnsmasq_add_static_address(popen_mock, dnsmasq_waiter,
                                    dnsmasq_reloader, tmp_path):
    paths = {
        'BOOTS_ROOT': tmp_path,
        'TFTP_DIR': f'{tmp_path}/tftp',
        'PXELINUX_CONFIG_DIR': f'{tmp_path}/pxelinux.cfg',
    }
    os.makedirs(paths['PXELINUX_CONFIG_DIR'])
    dnsmasq = Dnsmasq('br0', paths)
    dnsmasq.add_static_address('00:11:22:33:44:55',
                               '1.2.3.4',
                               'hostname')
    dnsmasq.add_static_address('00:11:22:33:44:66',
                               '1.2.3.5',
                               'hostname2')
    p = Path(paths['BOOTS_ROOT']) / "hosts.dhcp"
    assert p.read_text() == \
        """00:11:22:33:44:55,1.2.3.4,set:hostname
00:11:22:33:44:66,1.2.3.5,set:hostname2
"""
    assert len(dnsmasq_reloader.mock_calls) == 2


@patch("server.boots.Dnsmasq", autospec=True)
@patch("server.boots.provision_network_boot_service")
def test_bootservice(mock_provisioner, mock_dnsmasq, tmp_path):
    paths = {
        'BOOTS_ROOT': tmp_path,
        'TFTP_DIR': f'{tmp_path}/tftp',
        'PXELINUX_CONFIG_DIR': f'{tmp_path}/pxelinux.cfg',
    }
    os.makedirs(paths['PXELINUX_CONFIG_DIR'])
    service = BootService(private_interface='br0',
                          default_kernel='default_kernel',
                          default_initrd='default_initrd',
                          default_cmdline='default_cmdline',
                          config_paths=paths)
    mock_provisioner.assert_called_once()
    service.stop()
    service.dnsmasq.stop.assert_called_once()


@patch("server.boots.Dnsmasq", autospec=True)
@patch("server.boots.provision_network_boot_service")
def test_bootservice_write_config(mock_provisioner, mock_dnsmasq, tmp_path):
    paths = {
        'BOOTS_ROOT': tmp_path,
        'TFTP_DIR': f'{tmp_path}/tftp',
        'PXELINUX_CONFIG_DIR': f'{tmp_path}/pxelinux.cfg',
    }
    os.makedirs(paths['PXELINUX_CONFIG_DIR'])
    service = BootService(private_interface='br0',
                          default_kernel='default_kernel',
                          default_initrd='default_initrd',
                          default_cmdline='default_cmdline',
                          config_paths=paths)

    service.write_network_config('00:11:22:33:44:55',
                                 '1.2.3.4',
                                 'hostname')
    service.dnsmasq.add_static_address.assert_called_with(
        '00:11:22:33:44:55',
        '1.2.3.4',
        'hostname')

    service.write_pxelinux_config('default',
                                  'kernel_path',
                                  'cmdline',
                                  'initrd_path')
    p = Path(paths['PXELINUX_CONFIG_DIR']) / "default"
    assert p.read_text() == \
        """DEFAULT default
label default
  KERNEL kernel_path
  INITRD initrd_path
  APPEND cmdline"""

    service.write_pxelinux_config('00:11:22:33:44:55',
                                  'kernel_path',
                                  'cmdline',
                                  'initrd_path')
    p = Path(paths['PXELINUX_CONFIG_DIR']) / "01-00-11-22-33-44-55"
    assert p.read_text() == \
        """DEFAULT default
label default
  KERNEL kernel_path
  INITRD initrd_path
  APPEND cmdline"""

    service.stop()
    config_files = \
        glob.glob(os.path.join(paths['PXELINUX_CONFIG_DIR'], '01-*'))
    assert len(config_files) == 0


@patch("server.boots.Dnsmasq", autospec=True)
@patch("server.boots.provision_network_boot_service")
def test_bootservice_remove_config(mock_provisioner, mock_dnsmasq, tmp_path):
    paths = {
        'BOOTS_ROOT': tmp_path,
        'TFTP_DIR': f'{tmp_path}/tftp',
        'PXELINUX_CONFIG_DIR': f'{tmp_path}/pxelinux.cfg',
    }
    os.makedirs(paths['PXELINUX_CONFIG_DIR'])
    service = BootService(private_interface='br0',
                          default_kernel='default_kernel',
                          default_initrd='default_initrd',
                          default_cmdline='default_cmdline',
                          config_paths=paths)

    service.write_pxelinux_config('00:11:22:33:44:55',
                                  'kernel_path',
                                  'cmdline',
                                  'initrd_path')
    p = Path(paths['PXELINUX_CONFIG_DIR']) / "01-00-11-22-33-44-55"
    assert p.exists()

    service.remove_pxelinux_config('00:11:22:33:44:55')
    assert not p.exists()
