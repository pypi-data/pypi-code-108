#! /usr/bin/env python
# Copyright 2021 Cisco Systems Inc, All rights reserved.
import logging
import re

import lxml.etree as et
import pandas as pd
from django.utils.itercompat import is_iterable

from ysfilemanager import split_user_set, YSYangSet
from ysyangtree import YSContext, YSYangModels

log = logging.getLogger(__name__)


class CiscoConfig:
    """CiscoConfig normalizes CLI commands."""

    skip = ["enable", "config", "t", "configure", "end", "show",
            "terminal", "commit", "#", "!", "<rpc", "Building"]

    timestamps = ["mon", "tue", "wed", "thu", "fri", "sat", "sun", "jan",
                  "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
                  "oct", "nov", "dec"]

    timeregex = re.compile(
        "^(([0-1]?[0-9])|([2][0-3])):([0-5]?[0-9])(:([0-5]?[0-9]))?"
    )

    RE_INTERFACE_ID = re.compile(r'[^0-9/]')

    def _handle_intf(self, intf):
        # want this "interface GigabitEthernet 1/0/1"
        # might be this "interface GigabitEthernet1/0/1"
        intf_list = intf.split()
        if len(intf_list) == 3:
            return intf
        intf_list.remove('interface')
        intf = ''.join(intf_list)
        int_id = re.sub(self.RE_INTERFACE_ID, '', intf)
        intf = intf.replace(int_id, ' ')
        return "interface " + intf + int_id

    def _handle_username(self, username):
        # might be "username lab password 0 mypassword"
        # or "username lab password mypassword"
        return username.replace("password 0", "password", 1)

    def _handle_exit(self, line):
        # clear out "exit" if found
        if len(line.split()) == 1:
            return None
        return line

    special_handles = {"interface": _handle_intf,
                       "username": _handle_username,
                       "exit": _handle_exit}

    def _check_special_handles(self, line):

        if line.split()[0] in self.special_handles.keys():
            line = self.special_handles[line.split()[0]](self, line)
        return line

    def _check_timestamps(self, line):
        if line[:3].lower() in self.timestamps:
            for item in line.split():
                if self.timeregex.match(item):
                    return True
        return False

    def normalize(self, cfg='', skip_no=True):
        """Removes uninteresting CLI and returns structured data.

        Remove comments, organize blocks of config data,
        skip maintainence operations, and other tasks.

        NOTE: Copying and pasting a show running-config may have
        compare errors only specific to the show command so it is
        best to copy the config from device to file and use that text.

        Args:
          cfg (str): CLI text from a configuration copied off a Cisco device.
        Returns:
          listt: Configuration lines of interest.
        """
        clean_cfg = []

        for line in cfg.splitlines():

            if not line.split():
                # empty line
                continue
            if "--More--" in line:
                # pick up anything that may be included after the "More"
                line = line[line.find('--More--') + 8:]
                if not line.split():
                    # emptied line
                    continue
            if line.startswith('#'):
                continue
            if line.startswith('!'):
                continue
            if line.startswith('Current configuration'):
                continue
            if line.rstrip().endswith("#"):
                continue
            if line.strip().startswith('no ') and skip_no:
                continue
            if line.split()[0] in self.skip:
                continue
            if self._check_timestamps(line):
                continue
            line = self._check_special_handles(line)
            if line is None:
                continue

            clean_cfg.append(line.strip())

        return clean_cfg


class ConfigXML:
    """Determine association of CLI config to XML."""

    def __init__(self, cli, xml, yangset=None, dataset=None):
        self.cli = cli
        self.yangset = yangset
        self.dataset = dataset
        self.xml = xml

    def _get_module(self, nspcs):
        modules = set()
        for nspace in nspcs:
            if "/Cisco-IOS-" in nspace:
                module = nspace[nspace.rfind("/") + 1 :]
            elif "/cisco-nx" in nspace:  # NXOS lowercases namespace
                module = "Cisco-NX-OS-device"
            elif "/openconfig.net" in nspace:
                module = "openconfig-"
                module += nspace[nspace.rfind("/") + 1 :]
            elif "urn:ietf:params:xml:ns:yang:" in nspace:
                module = nspace.replace("urn:ietf:params:xml:ns:yang:", "")
            if module:
                modules.add(module)
        return list(modules)

    @property
    def cli(self):
        return self._cli

    @cli.setter
    def cli(self, cli):
        self._original_cli = cli
        self._cli = CiscoConfig().normalize(cli)

    @property
    def xml(self):
        return self._xml

    @xml.setter
    def xml(self, xml):
        try:
            if et.iselement(xml):
                cfg = xml
            else:
                cfg = et.fromstring(xml)
            if hasattr(cfg, 'tag'):
                data = ''
                if cfg.tag.endswith('rpc-reply'):
                    data = cfg[0]
                elif cfg.tag.endswith('data'):
                    data = cfg
                elif cfg.tag.endswith('rpc'):
                    for el in cfg.iter():
                        if not el.tag.endswith('-config') and \
                                el.tag.endswith('config'):
                            data = el
                            break
                    else:
                        data = cfg[0]
                if len(data):
                    self._xml = data[0]
                    # remove parents
                    if et.iselement(self._xml.getparent()):
                        self._xml.getparent().remove(self._xml)
                    models = set()
                    for el in self._xml.iter():
                        nspc = el.nsmap.values()
                        models.update(self._get_module(nspc))
                    models = list(models)
                    if self.yangset and self.dataset is None:
                        user, yset = split_user_set(self.yangset)
                        ctx = YSContext.get_instance(user, self.yangset)
                        if not ctx:
                            repo = YSYangSet.load(user, yset)
                            ctx = YSContext(repo, user, models)
                        self.dataset = YSYangModels(ctx, models)
                else:
                    self._xml = None

        except et.XMLSyntaxError:
            log.error('Invalid XML for rpc-reply')
            self._xml = None

    def get_endpoints(self):
        if not et.iselement(self.xml):
            return [], []

        xml_endpoints = []
        prev_xp = ''
        prev_modules = []
        for i in self.xml.iter():
            xp = self.get_xpath(i)
            modules = self._get_module(i.nsmap.values())
            if prev_xp and prev_xp in xp and prev_xp != xp:
                if (prev_xp, '', prev_modules) in xml_endpoints:
                    xml_endpoints.remove((prev_xp, '', prev_modules))
            if i.text and i.text.strip():
                xml_endpoints.append((xp, i.text.strip(), modules))
            else:
                xml_endpoints.append((xp, '', modules))

            prev_xp = xp
            prev_modules = modules

        cli_endpoints = []
        for line in self.cli:
            ln = line.split()
            cli_endpoints.append((ln, ln[len(ln) - 1]))

        return (xml_endpoints, cli_endpoints)

    def match_endpoints(self, xml_ends, cli_ends):
        matched_ends = []
        if not xml_ends or not is_iterable(xml_ends):
            log.error('Can not iterate XML endpoints')
            return matched_ends
        if not cli_ends or not is_iterable(cli_ends):
            log.error('Can not iterate CLI endpoints')
            return matched_ends

        for xp, val, modules in xml_ends:
            if len(val.split()) > 1:
                val_list = val.split()
                val = val_list[-1]
            else:
                val_list = []
            for cli, cfg in cli_ends:
                presence_or_empty = False
                if val == cfg:
                    if val_list:
                        if not set(val_list).issubset(cli):
                            continue
                    matched_ends.append((xp, ' '.join(cli), modules))
                    cli_ends.remove((cli, cfg))
                    break
                elif not val and self.dataset and \
                        [m for m in modules if m in self.dataset.yangs]:
                    for mod, ds in self.dataset.yangs.items():
                        node = ds.tw.get_node_by_xpath(xp, no_prefix=True)
                        if not node:
                            continue
                        if 'presence' in node['data'] or node['data']['datatype'] == 'empty':
                            matched_ends.append((xp, ' '.join(cli), mod))
                            cli_ends.remove((cli, cfg))
                            presence_or_empty = True
                            break
                    else:
                        print('NOT FOUND {0}'.format(xp))
                        break
                elif not val:
                    if xp.split('/')[-1] == cli[-1]:
                        matched_ends.append((xp, ' '.join(cli), modules))
                        cli_ends.remove((cli, cfg))
                if presence_or_empty:
                    break

        return matched_ends

    def get_xpath(self, elem):
        xpath = []
        for el in self.xml.iter():
            if el != elem:
                continue
            parent = el.getparent()
            xpath.append('/' + et.QName(el).localname)
            while True:
                if parent is not None:
                    xpath.append('/' + et.QName(parent).localname)
                    parent = parent.getparent()
                else:
                    break

            return ''.join(reversed(xpath))


if __name__ == '__main__':
    xml = open('tests/fixtures/rpc/ddmi-2-9500.edit.cfg').read()
    cli = open('tests/fixtures/cli/ddmi-2-9500.cfg').read()
    cfgx = ConfigXML(cli, xml)
    xml_ends, cli_ends = cfgx.get_endpoints()
    xpath_cli = cfgx.match_endpoints(xml_ends, cli_ends)
    from pprint import pprint as pp
    pp(xpath_cli)
    print('ENTRY TOTAL COUNT {0}'.format(len(xpath_cli)))
