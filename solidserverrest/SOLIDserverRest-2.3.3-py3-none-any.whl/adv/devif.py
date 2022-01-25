# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 13:49:28 alex>
#

"""
SOLIDserver device manager host interface

"""

import logging
import ipaddress
import time
import re

from SOLIDserverRest.Exception import SDSError
from SOLIDserverRest.Exception import SDSDeviceIfError
from SOLIDserverRest.Exception import SDSDeviceIfNotFoundError

from .class_params import ClassParams
from .device import Device
from .space import Space


# pylint: disable=R0902
class DeviceInterface(ClassParams):
    """ class to manipulate the SOLIDserver device interface """

    # -------------------------------------
    def __init__(self, sds=None, name=None, device=None, class_params=None):
        """init a device interface object:
        - sds: object SOLIDserver, could be set afterwards
        - name: name of the interface
        - device: reference to a Device object
        """

        if name is None:
            raise SDSDeviceIfError("no name provided at device interface init")

        if device is None or not isinstance(device, Device):
            raise SDSDeviceIfError("no device provided")

        if device.myid == -1:
            raise SDSDeviceIfError("device should be linked in SDS")

        super().__init__()

        # params mapping the object in SDS
        self.clean_params()

        self.set_sds(sds)
        self.set_name(name)
        self.set_device(device)

        self.ipv4 = None
        self.ipv6 = None
        self.mac = None

        self.space = None

        self.type = "interface"

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def clean_params(self):
        """ clean the object params """
        super().clean_params()

        self.params = {
            'hostiface_id': None,
            'hostiface_name': None,
            'hostdev_id': None,
            'modify_time': None,
        }

        self.device = None
        self.ipv4 = None
        self.ipv6 = None
        self.mac = None
        self.space = None
        self.type = "interface"

    # -------------------------------------
    def set_param(self, param=None, value=None, exclude=None, name=None):
        super().set_param(param,
                          value,
                          exclude=['hostiface_id'],
                          name='hostiface_name')

    # -------------------------------------
    def create(self):
        """ create the device interface in SDS """

        if self.sds is None:
            raise SDSDeviceIfError(message="not connected")

        params = {
            'hostiface_name': self.name,
            'hostdev_id': self.device.myid,
            'hostiface_type': self.type,
            **self.additional_params
        }

        if self.ipv4 is not None:
            params['hostiface_addr'] = self.ipv4

        if self.mac is not None:
            params['hostiface_mac'] = self.mac

        if (self.space is not None
                and isinstance(self.space, Space)
                and self.space.myid != -1):
            params['site_id'] = self.space.myid
        else:
            logging.warning("no space set on interface")

        self.prepare_class_params('hostiface', params)

        # logging.info(params)

        rjson = self.sds.query("host_iface_create",
                               params=params)

        if 'errmsg' in rjson:
            raise SDSDeviceIfError(message="devif creation error, "
                                   + rjson['errmsg'])

        self.params['hostiface_id'] = int(rjson[0]['ret_oid'])
        self.myid = int(self.params['hostiface_id'])

        self.refresh()

    # -------------------------------------
    def update(self):
        """ update the device interface in SDS """

        if self.sds is None:
            raise SDSDeviceIfError(message="not connected")

        params = {
            'hostiface_id': self._get_id(query="host_iface_list",
                                         key="hostiface"),
            'hostiface_name': self.name,
            'modify_time': int(time.time()),
            **self.additional_params
        }

        if self.ipv4 is not None:
            params['hostiface_addr'] = self.ipv4

        self.prepare_class_params('hostiface', params)

        rjson = self.sds.query("host_iface_update",
                               params=params)

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSDeviceIfError(message="interface update error, "
                                   + rjson['errmsg'])

        self.refresh()

    # -------------------------------------
    def delete(self):
        """deletes the device interface in the SDS"""
        if self.sds is None:
            raise SDSDeviceIfError(message="not connected")

        if self.myid == -1:
            raise SDSDeviceIfNotFoundError("on delete")

        params = {
            'hostiface_id': self.myid,
            **self.additional_params
        }

        rjson = self.sds.query("host_iface_delete",
                               params=params)

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSDeviceIfNotFoundError("on delete "+rjson['errmsg'])

        self.clean_params()

    # -------------------------------------
    def refresh(self):
        """refresh content of the device interface from the SDS"""

        if self.sds is None:
            raise SDSDeviceIfError(message="not connected")

        if self.myid == -1:
            params = {
                **self.additional_params
            }

            params['WHERE'] = f"hostiface_name='{self.name}'"
            params['WHERE'] += " and hostdev_name"
            params['WHERE'] += f"='{self.device.name}'"

            try:
                rjson = self.sds.query("host_iface_list",
                                       params=params)
            except SDSError as err_descr:  # pragma: no cover
                msg = "cannot found object by name"
                msg += " / "+str(err_descr)
                raise SDSError(msg) from err_descr

            if rjson[0]['errno'] != '0':  # pragma: no cover
                raise SDSError("errno raised on get id by name")

            if_id = rjson[0]['hostiface_id']
        else:
            if_id = self.myid

        params = {
            "hostiface_id": if_id,
            **self.additional_params
        }

        try:
            rjson = self.sds.query("host_iface_info",
                                   params=params)
        except SDSError as err_descr:   # pragma: no cover
            msg = f"cannot get device interface info on id={if_id}"
            msg += " / "+str(err_descr)
            raise SDSDeviceIfError(msg) from err_descr

        rjson = rjson[0]
        # logging.info(rjson)

        for label in ['hostiface_id',
                      'hostiface_name',
                      'hostdev_id',
                      'iplnetdev_id',
                      'hostiface_type',
                      'hostiface_class_name',
                      'pear_iface_id',
                      'pear_ipl_iface_id',
                      'iplport_id',
                      'custom_db_data_id',
                      'hostiface_mac',
                      'add_time',
                      'modify_time',
                      'vendor_key',
                      'vendor_mac',
                      'hostiface_ip_formated',
                      'row_enabled',
                      'hostiface_site_id',
                      'hostiface_manual_link',
                      'hostiface_auto_link',
                      'nb_ip'
                      ]:
            if label not in rjson:  # pragma: no cover
                msg = f"parameter {label} not found in device"
                raise SDSDeviceIfError(msg)
            self.params[label] = rjson[label]

        self.myid = int(self.params['hostiface_id'])
        self.name = self.params['hostiface_name']

        if (int(self.params['hostdev_id'])
                != self.device.myid):  # pragma: no cover
            logging.error('interface has changed device - TODO')
            logging.error('%s / %s', self.device.myid,
                          self.params['hostdev_id'])

        if 'hostiface_class_parameters' in rjson:
            self.update_class_params(rjson['hostiface_class_parameters'])

        if 'hostiface_ip_formated' in rjson:
            # regexpip = re.compile('
            ip_raw = re.search(r'^(((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)'
                               '{3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
                               ' .*$',
                               rjson['hostiface_ip_formated'])

            if ip_raw:
                self.ipv4 = ip_raw.group(1)

        self.device.link_interface(self)

    # ---------------------------
    def set_device(self, dev):
        """set the device"""
        self.device = dev

    # ---------------------------
    def set_ipv4(self, addr):
        """set the ipv4 address on the interface"""
        self.ipv4 = None
        try:
            self.ipv4 = str(ipaddress.IPv4Address(addr))
        except ValueError as err:
            raise SDSDeviceIfError('bad ipv4 format') from err

    # ---------------------------
    def set_mac(self, mac):
        """set the mac address on the interface"""
        self.mac = None
        self.mac = str(mac)

    # ---------------------------
    def set_space(self, space):
        """set the space on the interface"""
        self.space = None
        if not isinstance(space, Space):
            raise SDSDeviceIfError("space incorect")

        if space.myid == -1:
            raise SDSDeviceIfError("space not synchronized")

        self.space = space

    # -------------------------------------
    def __str__(self):  # pragma: no cover
        """return the string notation of the device interface object"""

        return_val = f"*dev if* name={self.name}"

        if self.ipv4 is not None:
            return_val += f" ipv4={self.ipv4}"

        if self.ipv6 is not None:
            return_val += f" ipv6={self.ipv6}"

        return_val += self.str_params(exclude=['hostiface_id',
                                               'hostiface_name'])

        return_val += str(super().__str__())

        return return_val
