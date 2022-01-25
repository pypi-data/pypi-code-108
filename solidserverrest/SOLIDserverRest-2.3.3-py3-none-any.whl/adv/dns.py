#
# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 14:17:15 alex>
#

"""
SOLIDserver DNS server management

"""

import ipaddress
import logging
import time

from SOLIDserverRest.Exception import (SDSInitError,
                                       SDSError,
                                       SDSDNSError,
                                       SDSDNSAlreadyExistingError,
                                       SDSDNSCredentialsError)

from .class_params import ClassParams


class DNS(ClassParams):
    """ class to manipulate the SOLIDserver DNS object """

    # -------------------------------------
    def __init__(self, sds=None,
                 name=None,
                 class_params=None):
        """init the DNS object:
        - sds: object SOLIDserver, could be set afterwards
        - name: dns server name
        """

        super().__init__(sds, name)

        self.ipv4_addr = None
        self.insync_wait_time = 0.5

        self.params = {
            'aws_keyid': None,
            'dns_allow_query': None,
            'dns_allow_query_cache': None,
            'dns_allow_recursion': None,
            'dns_allow_transfer': None,
            'dns_also_notify': None,
            'dns_class_name': '',
            'dns_comment': None,
            'dns_forward': '',
            'dns_forwarders': '',
            'dns_id': None,
            'dns_key_name': None,
            'dns_key_proto': None,
            'dns_key_value': None,
            'dns_name': None,
            'dns_notify': None,
            'dns_recursion': 'yes',
            'dns_role': None,
            'dns_state': None,
            'dns_synching': None,
            'dns_type': None,
            'dns_version': None,
            'dnsblast_enabled': None,
            'dnsblast_status': None,
            'dnsgslb_supported': None,
            'dnsguardian_supported': None,
            'dnssec_validation': None,
            'gss_enabled': None,
            'gss_keytab_id': None,
            'ip_addr': None,
            'ipmdns_https_login': None,
            'ipmdns_https_password': None,
            'ipmdns_is_package': None,
            'ipmdns_protocol': 'https',
            'ipmdns_type': None,
            'isolated': '0',
            'ldap_domain': None,
            'ldap_password': None,
            'ldap_user': None,
            'multistatus': None,
            'querylog_state': None,
            'total_vdns_members': None,
            'vdns_arch': None,
            'vdns_members_name': None,
            'vdns_parent_arch': None,
            'vdns_parent_id': None,
            'vdns_parent_name': None,
            # 'vdns_public_ns_list': None,
        }

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def _get_dnsid_by_name(self, dnsname):
        """get the DNS server ID from its name,
           return None if non existant"""

        try:
            rjson = self.sds.query("dns_server_list",
                                   params={
                                       "WHERE": f"dns_name='{dnsname}'",
                                       **self.additional_params
                                   })
        except SDSError:
            return None

        if rjson[0]['errno'] != '0':
            raise SDSDNSError("dns_id errno raised")

        return rjson[0]['dns_id']

    # -------------------------------------
    def set_ipv4(self, ipv4=None):
        ''' set ipv4 address of the DNS server'''
        try:
            self.ipv4_addr = ipaddress.IPv4Address(ipv4)
        except ipaddress.AddressValueError as err:
            raise SDSDNSError(message='bad IPv4 address'
                              ' for DNS server') from err

    # -------------------------------------
    def set_type(self, newtype=None, vdns_arch=None):
        '''set type of the DNS server'''
        if newtype not in ['ipm', 'msdaemon', 'ans', 'aws', 'other', 'vdns']:
            raise SDSDNSError(message='bad DNS type')

        self.params['dns_type'] = newtype

        if newtype == 'vdns':
            if not vdns_arch:
                raise SDSDNSError(message='SMARTarchitecture needs type')
            if vdns_arch not in ['masterslave',
                                 'stealth',
                                 'multimaster',
                                 'single',
                                 'farm']:
                raise SDSDNSError(message='bad SMARRTarchitecture type')
            self.params['vdns_arch'] = vdns_arch

    # -------------------------------------
    def set_ipm_credentials(self, user, passwd):
        '''set admin credentials to talk to a ipmdns'''
        self.params['ipmdns_https_login'] = user
        self.params['ipmdns_https_password'] = passwd

    # -------------------------------------
    def _update_params(self, params):
        if self.params['dns_forward'] is not None:
            params['dns_forward'] = self.params['dns_forward']
            params['dns_forwarders'] = self.params['dns_forwarders']
        else:  # pragma: no cover
            params['dns_forward'] = ''
            params['dns_forwarders'] = ''

        if self.params['dns_recursion'] is None:   # pragma: no cover
            params['dns_recursion'] = 'yes'
        else:
            params['dns_recursion'] = self.params['dns_recursion']

    # -------------------------------------
    def create(self):
        """creates the DNS server"""
        if self.sds is None:
            raise SDSInitError(message="not connected")

        dns_id = self._get_dnsid_by_name(self.name)
        if dns_id is not None:
            raise SDSDNSAlreadyExistingError(message="already"
                                             + " existant dns server")

        if self.params['dns_type'] is None:
            raise SDSDNSError(message="DNS server"
                              + " with bad type, use set_type")

        params = {
            'dns_name': self.name,
            'dns_type': self.params['dns_type'],
            **self.additional_params
        }

        if self.params['dns_type'] != 'vdns':
            if self.ipv4_addr is None:
                raise SDSDNSError(message="DNS server"
                                  + " without IP address, use set_ipv4")
            params['hostaddr'] = self.ipv4_addr

            if self.params['dns_type'] == 'ipm':
                params['ipmdns_https_login'] = self.params[
                    'ipmdns_https_login']
                params['ipmdns_https_password'] = self.params[
                    'ipmdns_https_password']

        else:
            params['vdns_arch'] = self.params['vdns_arch']

        self._update_params(params)

        self.prepare_class_params('dns', params)

        try:
            rjson = self.sds.query("dns_server_create",
                                   params=params)
        except SDSError as err:   # pragma: no cover
            raise SDSDNSError(message="create DNS server") from err

        if 'errno' in rjson:   # pragma: no cover
            if rjson['errno'] == '14401':
                raise SDSDNSCredentialsError(message=rjson['errmsg'])

            logging.info(rjson)
            raise SDSDNSError(message="DNS creation error: "
                              + rjson['errmsg'])

        if 'ret_oid' not in rjson[0]:   # pragma: no cover
            raise SDSDNSError(message="DNS server creation error "
                              + rjson['errmsg'])

        self.params['dns_id'] = int(rjson[0]['ret_oid'])
        self.myid = self.params['dns_id']

        self.refresh()

    # -------------------------------------
    def delete(self):
        """deletes the DNS server in the SDS"""
        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.myid is None or self.myid == -1:
            raise SDSDNSError(message="missing DNS id")

        self._wait_for_synch(self.myid)

        try:
            rjson = self.sds.query("dns_server_delete",
                                   params={
                                       'dns_id': self.myid,
                                       **self.additional_params
                                   })
            if 'errmsg' in rjson:  # pragma: no cover
                raise SDSDNSError(message="DNS server delete error, "
                                  + rjson['errmsg'])
        except SDSError as err:
            raise SDSDNSError(message="DNS server"
                              " delete error") from err

        self.myid = -1

    # -------------------------------------
    def _wait_for_synch(self, dns_id=None):
        """waith for the DNS server to be in sync"""
        if dns_id is None:  # pragma: no cover
            return None

        _wait_delay = self.insync_wait_time

        for retry in range(10):
            rjson = self.sds.query("dns_server_info",
                                   params={
                                       "dns_id": dns_id,
                                   })

            if not rjson:   # pragma: no cover
                raise SDSDNSError(message="DNS in sync error")

            if rjson[0]['dns_synching'] == '0':
                if retry > 0:
                    self.insync_wait_time *= 1.2
                else:
                    self.insync_wait_time /= 1.1
                return rjson

            # logging.info('not in synch {}'.format(_wait_delay))
            time.sleep(_wait_delay)
            _wait_delay *= 2

        return None  # pragma: no cover

    # -------------------------------------
    def refresh(self):
        """refresh content of the DNS from the SDS"""
        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.myid is None or self.myid == -1:
            dns_id = self._get_dnsid_by_name(self.name)
        else:
            dns_id = self.myid

        if dns_id is None:
            raise SDSDNSError(message="non existant DNS to refresh")

        rjson = self._wait_for_synch(dns_id)

        if not rjson:   # pragma: no cover
            raise SDSDNSError(message="DNS server refresh error, len of array")

        rjson = rjson[0]

        for label in [
                'aws_keyid',
                'dns_allow_query',
                'dns_allow_query_cache',
                'dns_allow_recursion',
                'dns_allow_transfer',
                'dns_also_notify',
                'dns_class_name',
                'dns_comment',
                'dns_forward',
                'dns_forwarders',
                'dns_hybrid',
                'dns_id',
                'dns_key_name',
                'dns_key_proto',
                'dns_key_value',
                'dns_name',
                'dns_notify',
                'dns_recursion',
                'dns_role',
                'dns_state',
                'dns_synching',
                'dns_type',
                'dns_version',
                'dnsblast_enabled',
                'dnsblast_status',
                'dnsgslb_supported',
                'dnsguardian_supported',
                'dnssec_validation',
                'gss_enabled',
                'gss_keytab_id',
                'ipmdns_is_package',
                'ipmdns_type',
                'isolated',
                'multistatus',
                'querylog_state',
                'vdns_arch',
                'vdns_members_name',
                'vdns_parent_name',
                'vdns_parent_id',
        ]:
            if label not in rjson:   # pragma: no cover
                raise SDSDNSError(f"parameter {label}"
                                  + " not found in DNS server")
            self.params[label] = rjson[label]

        if self.params['dns_type'] != 'vdns':
            self.ipv4_addr = ipaddress.IPv4Address(int(rjson['ip_addr'], 16))

        self.myid = int(self.params['dns_id'])

        if 'dns_class_parameters' in rjson:
            self.update_class_params(rjson['dns_class_parameters'])

    # -------------------------------------
    def update(self):
        """ update the DNS server """

        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.myid is None or self.myid == -1:
            dns_id = self._get_dnsid_by_name(self.name)
        else:
            dns_id = self.myid

        if dns_id is None:
            raise SDSDNSError(message="non existant DNS to refresh")

        params = {
            'dns_id': dns_id,
            **self.additional_params
        }

        self._update_params(params)

        self.prepare_class_params('dns', params)

        # logging.info(params)

        rjson = self.sds.query("dns_server_update",
                               params=params)

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSDNSError(message="DNS server update error, "
                              + rjson['errmsg'])

        self.refresh()

    # -------------------------------------
    def set_forward(self, mode=None, targets=None):
        """ update the DNS server forwarders
            mode is: None, only or first
            targets is an array with ip addresses of targets as string
        """
        if mode is None:
            self.params['dns_forward'] = ''
            self.params['dns_forwarders'] = ''
        else:
            if mode in ['only', 'first']:
                self.params['dns_forward'] = mode
                self.params['dns_forwarders'] = ";".join(targets)
            else:
                raise SDSDNSError("bad forwarder type")  # pragma: no cover

    # -------------------------------------
    def set_recursion(self, mode=False):
        """ update the DNS server recursion mode
        """
        if mode:
            self.params['dns_recursion'] = 'yes'
        else:
            self.params['dns_recursion'] = 'no'

    # -------------------------------------
    def __str__(self):
        """return the string notation of the DNS server object"""
        return_val = f"*DNS* name={self.name}"

        if self.myid != -1:
            return_val += f" id={self.myid}"

        if self.ipv4_addr is not None:
            return_val += f" ip={self.ipv4_addr}"

        if self.params['dns_type'] == 'ipm':
            return_val += " ipm={}".format(str(self.params['ipmdns_type']))
        else:
            return_val += " type={}".format(str(self.params['dns_type']))

        if self.params['dns_recursion'] is not None:
            return_val += f" recursion={self.params['dns_recursion']}"

        if self.params['dns_forward'] in ['first', 'only']:
            return_val += " forward"
            return_val += f"[{self.params['dns_forward']}]"
            return_val += f"={self.params['dns_forwarders']}"

        return_val += f" notify={self.params['dns_notify']}"

        if self.params['dns_class_name'] != '':    # pragma: no cover
            return_val += " class="
            return_val += "{self.params['dns_class_name']}"

        return_val += str(super().__str__())

        return return_val
