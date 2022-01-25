#
# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 13:42:15 alex>
#

"""
SOLIDserver DNS record management

"""

# import logging
import time
import ipaddress
# import pprint

from SOLIDserverRest.Exception import (SDSInitError,
                                       SDSError,
                                       SDSDNSError,
                                       SDSEmptyError,
                                       SDSIpAddressError)

from .class_params import ClassParams
from .dns_zone import DNS_zone
from .sds import SDS


class DNS_record(ClassParams):  # pylint: disable=C0103
    """ class to manipulate a DNS record object, from a zone """
    # -------------------------------------

    def __init__(self, sds=None, name=None, rr_type=None,
                 class_params=None):
        """init the record object"""

        if sds and not isinstance(sds, SDS):
            raise SDSInitError(message="sds param is not of type SDS")

        super().__init__(sds, name)

        self.zone = None
        self.ttl = 3600
        self.values = {}
        self.rr_type = None

        if rr_type:
            self.rr_type = str(rr_type)

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def set_zone(self, zone):
        """ link the record to a zone on the dns server """
        if not isinstance(zone, DNS_zone):
            raise SDSDNSError(message="record needs to be attached to a zone")

        self.zone = zone

    # -------------------------------------
    def set_type(self, rr_type, **kvargs):
        """ set the type for the record
            args depending on record type:
             * A/AAAA: ip
             * MX: priority, target
             * TXT: txt
             * NS: target
             * CNAME: target
        """

        self.rr_type = str(rr_type)

        # logging.info(kvargs)

        if len(kvargs) == 0:
            return

        if self.rr_type == 'A':
            self.set_values([kvargs['ip']])
        elif self.rr_type == 'AAAA':
            self.set_values([kvargs['ip']])
        elif self.rr_type == 'MX':
            self.set_values([kvargs['priority'],
                             kvargs['target']])
        elif self.rr_type == 'TXT':
            self.set_values([kvargs['txt']])
        elif self.rr_type == 'NS':
            self.set_values([kvargs['target']])
        elif self.rr_type == 'CNAME':
            self.set_values([kvargs['target']])

    # -------------------------------------

    def set_values(self, avalues):
        """ set the values depending on the record type """
        if not self.rr_type:
            raise SDSDNSError(message='need to set type of'
                              ' record before values')

        if self.rr_type == 'A':
            # check v1 is an ip address
            try:
                ipaddress.IPv4Address(avalues[0])
            except ipaddress.AddressValueError as err:
                raise SDSInitError(message="record A requires"
                                   + " an IP address") from err

            self.values = {
                '1': avalues[0]
            }

        elif self.rr_type == 'AAAA':
            # check v1 is an ip address
            try:
                ipaddress.IPv6Address(avalues[0])
            except ipaddress.AddressValueError as err:
                raise SDSInitError(message="record A "
                                   + "requires an IP address") from err

            self.values = {
                '1': avalues[0]
            }

        elif self.rr_type == 'TXT':
            self.values = {
                '1': str(avalues[0])
            }

        elif self.rr_type == 'NS':
            self.values = {
                '1': str(avalues[0])
            }

        elif self.rr_type == 'CNAME':
            self.values = {
                '1': str(avalues[0])
            }

        elif self.rr_type == 'MX':
            self.values = {
                '1': int(avalues[0]),
                '2': str(avalues[1])
            }

        else:
            raise SDSDNSError(message="unknown type"
                              f" of record {self.rr_type}")

    # -------------------------------------
    def set_ttl(self, ttl):
        """ set the ttl for this record """

        self.ttl = max(int(ttl), 5)

    # -------------------------------------
    def create(self, sync=True):
        """creates the DNS record in the zone"""
        if self.sds is None:
            raise SDSInitError(message="not connected")

        if self.zone is None:
            raise SDSDNSError(message="zone not attached")

        if not self.rr_type:
            raise SDSDNSError(message="record type not set")

        if '1' not in self.values:
            raise SDSDNSError(
                message=f"no values set for record {self.rr_type}")

        params = {
            'rr_name': self.name,
            'rr_type': self.rr_type,
            'dns_id': self.zone.dns_server.myid,
            'dnszone_id': self.zone.myid,
            'rr_ttl': str(self.ttl),
            'value1': self.values['1'],
            **self.additional_params
        }

        for _v in ['2', '3', '4', '5', '6', '7']:
            if _v in self.values:
                params[f'value{_v}'] = self.values[_v]

        self.prepare_class_params('rr', params)

        try:
            rjson = self.sds.query("dns_rr_create",
                                   params=params)
        except SDSError as err:   # pragma: no cover
            raise SDSDNSError(message="create DNS record") from err

        # logging.info(rjson)
        if 'errno' in rjson and int(rjson['errno']) > 0:
            raise SDSDNSError(message="record:"
                              f" {rjson['errmsg']}")

        rjson = rjson[0]
        if 'ret_oid' in rjson:
            self.myid = int(rjson['ret_oid'])

        if sync:
            self.refresh()

    # -------------------------------------
    def _wait_for_synch(self, delete=False):
        """wait for the DNS record to be in sync"""
        if self.myid is None or self.myid == -1:
            raise SDSDNSError(message="missing DNS record id")

        _wait_delay = 0.01

        for _ in range(10):
            try:
                rjson = self.sds.query("dns_rr_info",
                                       params={
                                           "rr_id": self.myid,
                                       })
            except SDSEmptyError:
                if delete:
                    return None

                time.sleep(_wait_delay)
                continue
            except SDSError:
                return None

            if not rjson:   # pragma: no cover
                raise SDSDNSError(message="DNS record sync error")

            if not delete:
                # we wait for the zone to be pushed to the server
                if rjson[0]['delayed_create_time'] == '0':
                    return rjson
            else:
                # we wait for the zone to be deleted from the server
                if rjson[0]['delayed_delete_time'] == '0':
                    return None

            # logging.info('not yet in synch %s %f', self.name, _wait_delay)
            _wait_delay *= 2
            time.sleep(_wait_delay)

        raise SDSDNSError(message="DNS record"
                          " sync takes too long")

    # -------------------------------------
    def refresh(self):
        """refresh content of the DNS record from the SDS"""
        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.zone is None:
            raise SDSDNSError(message="zone not attached")

        if self.myid is None or self.myid == -1:
            self.set_additional_where_params(rr_type=self.rr_type)
            self.set_additional_where_params(dns_id=self.zone.dns_server.myid)
            self.set_additional_where_params(dnszone_name=self.zone.name)

            rr_id = self._get_id_by_name('dns_rr_list',
                                         'rr_full',
                                         self.name,
                                         key_id='rr')

            self.clean_additional_where_params()
        else:
            rr_id = self.myid

        if rr_id is None:
            raise SDSDNSError(message="non existant DNS record to refresh")

        self.myid = rr_id
        rjson = self._wait_for_synch()

        if not rjson:   # pragma: no cover
            raise SDSDNSError(message="DNS record refresh error, len of array")

        rjson = rjson[0]

        for label in [
                'dns_class_name',
                'dns_cloud',
                'dns_comment',
                'dns_type',
                'dns_version',
                'rr_class_name',
                'rr_full_name_utf',
                'rr_glue',
                'ttl',
                'value1',
                'value2',
                'value3',
                'value4',
                'value5',
                'value6',
                'value7'
        ]:
            if label not in rjson:   # pragma: no cover
                raise SDSDNSError("parameter"
                                  + f" {label}"
                                  + " not found in DNS zone")
            self.params[label] = rjson[label]

        if 'rr_class_parameters' in rjson:
            self.update_class_params(rjson['rr_class_parameters'])

        self.ttl = int(rjson['ttl'])
        self.set_values([rjson['value1'],
                         rjson['value2'],
                         rjson['value3'],
                         rjson['value4'],
                         rjson['value5'],
                         rjson['value6'],
                         rjson['value7']])

    # -------------------------------------
    def delete(self, sync=True):
        """deletes the DNS record from the zone"""
        if self.sds is None:
            raise SDSDNSError(message="not connected")

        if self.myid is None or self.myid == -1:
            raise SDSDNSError(message="missing DNS RR id")

        try:
            rjson = self.sds.query("dns_rr_delete",
                                   params={
                                       'rr_id': self.myid,
                                       **self.additional_params
                                   })
            if 'errmsg' in rjson:  # pragma: no cover
                raise SDSDNSError(message="DNS record delete, "
                                  + rjson['errmsg'])
        except SDSError as err:
            raise SDSDNSError(message="DNS record delete error") from err

        if sync:
            time.sleep(0.1)
            self._wait_for_synch(delete=True)

        self.myid = -1

    # -------------------------------------
    def update(self):
        """ update the record in SDS """

        if self.sds is None:
            return

        if self.zone is None:
            return

        if not self.rr_type:
            return

        if '1' not in self.values:
            return

        params = {
            'rr_id': self.myid,
            'rr_ttl': str(self.ttl),
            'value1': self.values['1'],
            **self.additional_params
        }

        for _v in ['2', '3', '4', '5', '6', '7']:
            if _v in self.values:
                params[f'value{_v}'] = self.values[_v]

        self.prepare_class_params('rr', params)

        # logging.info(params)

        rjson = self.sds.query("dns_rr_update",
                               params=params)

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSIpAddressError(message="rr update error, "
                                    + rjson['errmsg'])

        self.refresh()

    # -------------------------------------
    def __str__(self):
        """return the string notation of the DNS record object"""
        return_val = f"*RR* name={self.name}"

        if self.myid and self.myid != -1:
            return_val += f" [#{self.myid}]"

        if self.zone:
            return_val += f" server={self.zone.dns_server.name}"
            return_val += f" zone={self.zone.name}"

        if self.rr_type:
            return_val += f" {self.rr_type}"
            if self.rr_type == 'A':
                if '1' in self.values:
                    return_val += f"={self.values['1']}"

            return_val += f" ttl={self.ttl}"

            if 'rr_glue' in self.params:
                return_val += f" glue={self.params['rr_glue']}"

        return_val += str(super().__str__())

        return return_val
