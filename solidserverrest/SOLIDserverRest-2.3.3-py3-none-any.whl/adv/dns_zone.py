#
# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 13:37:30 alex>
#

"""
SOLIDserver DNS zone management

"""

# import ipaddress
import logging
import time

from SOLIDserverRest.Exception import (SDSInitError,
                                       SDSError,
                                       SDSDNSError)

from .class_params import ClassParams
from .dns import DNS
from .sds import SDS


class DNS_zone(ClassParams):  # pylint: disable=C0103
    """ class to manipulate a DNS zone object """
    TYPE_MASTER = "master"
    TYPE_SLAVE = "slave"
    TYPE_HINT = "hint"
    TYPE_STUB = "stub"
    TYPE_FWD = "forward"
    TYPE_DELONLY = "delegation-only"
    TYPE_CLOUD = "cloud"

    TYPES_LIST = [TYPE_SLAVE,
                  TYPE_MASTER,
                  TYPE_HINT,
                  TYPE_STUB,
                  TYPE_FWD,
                  TYPE_DELONLY,
                  TYPE_CLOUD]

    # -------------------------------------

    def __init__(self, sds=None,
                 name=None,
                 zone_type=None,
                 class_params=None):
        """init the DNS zone object:
        - sds: object SOLIDserver, could be set afterwards
        - name: dns zone name
        - zone_type: dns zone type (master, slave, hint,
                                    stub, forward, delegation-only,
                                    cloud)
        - zone_resolution: ?
        """

        if sds and not isinstance(sds, SDS):
            raise SDSInitError(message="sds param is not of type SDS")

        super().__init__(sds, name)

        self.zone_type = None
        self.dns_server = None

        if zone_type:
            # TODO add checks  pylint: disable=W0511
            if zone_type not in self.TYPES_LIST:
                raise SDSDNSError(message="zone type unknown")
            self.zone_type = zone_type

        self.params = {
            'dnszone_is_reverse': 0
        }

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def set_dns(self, dns):
        """ link the zone to a dns server object """
        if not isinstance(dns, DNS):
            raise SDSDNSError(message="zone for linking is not a zone object")

        self.dns_server = dns

    # -------------------------------------
    def set_type(self, zone_type):
        """ set the type for the zone """

        if str(zone_type) not in self.TYPES_LIST:
            raise SDSDNSError(message="zone type not supported")

        self.zone_type = str(zone_type)

    # -------------------------------------
    def set_is_reverse(self, reverse_flag):
        """ set if the zone is reverse """

        if reverse_flag:
            self.params['dnszone_is_reverse'] = 1

    # -------------------------------------
    def create(self, sync=True):
        """creates the DNS zone"""
        if self.sds is None:
            raise SDSInitError(message="not connected")

        if self.dns_server is None:
            raise SDSDNSError(message="zone not linked to a DNS server")

        if self.zone_type not in self.TYPES_LIST:
            raise SDSDNSError(message="zone type not set")

        params = {
            'dnszone_name': self.name,
            'dnszone_type': self.zone_type,
            'dns_id': self.dns_server.myid,
            **self.additional_params
        }

        self.prepare_class_params('dnszone', params)

        try:
            rjson = self.sds.query("dns_zone_create",
                                   params=params)
        except SDSError as err:   # pragma: no cover
            raise SDSDNSError(message="create DNS zone") from err

        if 'errno' in rjson:
            raise SDSDNSError(message="create DNS zone"
                              f" {rjson['errmsg']}")

        rjson = rjson[0]
        if 'ret_oid' in rjson:
            self.myid = int(rjson['ret_oid'])

        if sync:
            time.sleep(.5)
            self.refresh()

    # -------------------------------------
    def _wait_for_synch(self, delete=False):
        """waith for the DNS zone to be in sync"""
        if self.myid is None or self.myid == -1:
            raise SDSDNSError(message="missing DNS id")

        _wait_delay = 2.0

        for _ in range(10):
            try:
                rjson = self.sds.query("dns_zone_info",
                                       params={
                                           "dnszone_id": self.myid,
                                       })
            except SDSError:
                return None

            if not rjson:   # pragma: no cover
                raise SDSDNSError(message="DNS zone sync error")

            if not delete:
                # we wait for the zone to be pushed to the server
                if rjson[0]['delayed_create_time'] == '0':
                    return rjson
            else:
                # we wait for the zone to be deleted from the server
                if rjson[0]['delayed_delete_time'] == '0':
                    return None

            logging.debug('not yet in synch %d', _wait_delay)
            time.sleep(_wait_delay)
            _wait_delay *= 1.2

        raise SDSDNSError(message="DNS zone sync takes too long")

    # -------------------------------------
    def delete(self, sync=True):
        """deletes the DNS zone from the server"""
        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.myid is None or self.myid == -1:
            raise SDSDNSError(message="missing DNS id")

        try:
            logging.debug("delete")
            rjson = self.sds.query("dns_zone_delete",
                                   params={
                                       'dnszone_id': self.myid,
                                       **self.additional_params
                                   })
            if 'errmsg' in rjson:  # pragma: no cover
                raise SDSDNSError(message="DNS zone delete error, "
                                  + rjson['errmsg'])
        except SDSError as err:
            raise SDSDNSError(message="DNS zone delete error") from err

        if sync:
            time.sleep(2)
            self._wait_for_synch(delete=True)

        self.myid = -1

    # -------------------------------------
    def refresh(self):
        """refresh content of the DNS zone from the SDS"""
        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.dns_server is None:
            raise SDSDNSError(message="zone not linked to a server")

        if self.myid is None or self.myid == -1:
            self.set_additional_where_params(dns_id=self.dns_server.myid)

            zone_id = self._get_id_by_name('dns_zone_list',
                                           'dnszone',
                                           self.name)

            self.clean_additional_where_params()
        else:
            zone_id = self.myid

        if zone_id is None:
            raise SDSDNSError(message="non existant DNS zone to refresh")

        self.myid = zone_id
        rjson = self._wait_for_synch()

        if not rjson:   # pragma: no cover
            raise SDSDNSError(message="DNS server refresh error, len of array")

        rjson = rjson[0]

        for label in [
                'dns_state',
                'dnszone_ad_integrated',
                'dnszone_allow_query',
                'dnszone_allow_transfer',
                'dnszone_allow_update',
                'dnszone_also_notify',
                'dnszone_class_name',
                'dnszone_forward',
                'dnszone_forwarders',
                'dnszone_is_reverse',
                'dnszone_is_rpz',
                'dnszone_masters',
                'dnszone_name',
                'dnszone_name_utf',
                'dnszone_notify',
                'dnszone_order',
                'dnszone_rev_sort_zone',
                'dnszone_type',
                'ds',
                'num_keys',
        ]:
            if label not in rjson:   # pragma: no cover
                raise SDSDNSError("parameter"
                                  + f" {label}"
                                  + " not found in DNS zone")
            self.params[label] = rjson[label]

        if 'dnszone_class_parameters' in rjson:
            self.update_class_params(rjson['dnszone_class_parameters'])

        self.zone_type = rjson['dnszone_type']

    # -------------------------------------
    def __str__(self):
        """return the string notation of the DNS zone object"""
        return_val = f"*ZONE* name={self.name}"

        if self.myid and self.myid != -1:
            return_val += f" [#{self.myid}]"

        if self.dns_server:
            return_val += f" server={self.dns_server.name}"

        if 'dnszone_is_reverse' in self.params:
            if self.params['dnszone_is_reverse'] == '1':
                return_val += " resolve=reverse"
            else:
                return_val += " resolve=name"
        else:
            return_val += " not refreshed"

        return_val += str(super().__str__())

        return return_val
