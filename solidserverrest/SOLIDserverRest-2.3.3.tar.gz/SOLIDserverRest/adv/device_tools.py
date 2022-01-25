# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 12:33:39 alex>
#

"""
SOLIDserver device manager

"""

import ipaddress
import re

# import logging
# import pprint
# import time

from SOLIDserverRest.Exception import SDSError, SDSInitError
from SOLIDserverRest.Exception import SDSDeviceError
from SOLIDserverRest.Exception import SDSEmptyError

# from .class_params import ClassParams
# from . import Device
# from . import DeviceInterface


# ------------------------------------------
def apply_filter_metadata(filt, dev_raw):
    """apply metadata value filter"""

    k = f"tag_hostdev_{filt['name']}"

    return dev_raw[k] == str(filt['val'])


# ------------------------------------------
def apply_filter_of_class(filt, dev_raw):
    """apply class parameter filter"""
    return dev_raw['hostdev_class_name'] == filt['val']


# ------------------------------------------
def apply_filter_in_subnet(filt, dev_raw):
    """apply ip address filter"""
    result = True

    if '_ipnet' not in filt:
        ipnet = ipaddress.ip_network(filt['val'])
        filt['_ipnet'] = ipnet
    else:
        ipnet = filt['_ipnet']

    if '_ipadd' not in dev_raw:
        dev_raw['_ipadd'] = []
        ip_raw = re.findall(r'(((25[0-5]|2[0-4][0-9]|[01]?'
                            r'[0-9][0-9]?)\.){3}(25[0-5]|'
                            r'2[0-4][0-9]|[01]?[0-9][0-9]?))',
                            dev_raw['hostdev_ip_formated'])
        for host_if_ip in ip_raw:
            if host_if_ip[0] not in dev_raw['_ipadd']:
                dev_raw['_ipadd'].append(host_if_ip[0])

    ip_raw = dev_raw['_ipadd']

    for host_if_ip in ip_raw:
        ipadd = ipaddress.ip_address(host_if_ip)

        if ipadd in ipnet:  # pylint: disable=R1723
            result = True
            break
        else:
            result = False

    return result


# ------------------------------------------
def apply_filter_space(filt, dev_raw):
    """apply space on ip address filter"""
    space_re = r'&([^,;]+)[,;]'

    spaces = re.findall(space_re, dev_raw['hostdev_ip_addr'])
    for space in spaces:
        if space == filt['val']:
            return True

    return False


# ------------------------------------------
def apply_list_filters(filters, dev_raw):
    """apply the list filters to the device and return True if all match"""
    result = True

    for filt in filters:
        if filt['type'] == "in_subnet":
            result = apply_filter_in_subnet(filt, dev_raw)
            if not result:
                return False

        if filt['type'] == "of_class":
            result = apply_filter_of_class(filt, dev_raw)
            if not result:  # pragma: no cover
                return False

        if filt['type'] == "metadata":
            result = apply_filter_metadata(filt, dev_raw)
            if not result:  # pragma: no cover
                return False

        if filt['type'] == "space":
            result = apply_filter_space(filt, dev_raw)
            if not result:
                return False

    return result


# ------------------------------------------
def _handle_filters(filters, _metadata_tags, _params):
    if filters is None:  # pragma: no cover
        filters = []

    # apply filters in the original query when possible
    for filt in filters:
        if filt['type'] == "of_class":
            _class_filter = "hostdev_class_name='{}'".format(filt['val'])
            if 'WHERE' in _params:
                _params['WHERE'] += " and " + _class_filter
            else:
                _params['WHERE'] = _class_filter

        if filt['type'] == "metadata" and filt['val'] not in _metadata_tags:
            _metadata_filter = f"hostdev.{filt['name']}"
            if 'TAGS' in _params:
                _params['TAGS'] += "&"+_metadata_filter
            else:
                _params['TAGS'] = _metadata_filter

            _metadata_filter = "tag_hostdev_{}='{}'".format(filt['name'],
                                                            str(filt['val']))
            if 'WHERE' in _params:
                _params['WHERE'] += " and " + _metadata_filter
            else:
                _params['WHERE'] = _metadata_filter

            _metadata_tags.append(filt['name'])


# ------------------------------------------
def _handle_metadata(_metadata_tags, _metadatas, _params):
    # expose metadata using TAGS
    if _metadatas:
        for _md in _metadatas:
            if _md not in _metadata_tags:
                _metadata_filter = f"hostdev.{_md}"
                if 'TAGS' in _params:
                    _params['TAGS'] += "&"+_metadata_filter
                else:
                    _params['TAGS'] = _metadata_filter


# ------------------------------------------
def list_devices_page(sds=None,
                      filters=None,
                      metadatas=None,
                      offset=0, page=25):
    """list devices from the space"""
    metadata_tags = []

    if sds is None:  # pragma: no cover
        raise SDSInitError("list device requires connection")

    params = {
        'limit': page,
        'offset': offset
    }

    _handle_filters(filters, metadata_tags, params)
    _handle_metadata(metadata_tags, metadatas, params)

    try:
        rjson = sds.query("host_device_list",
                          params=params)
    except SDSEmptyError:
        return None

    if 'errmsg' in rjson:  # pragma: no cover
        raise SDSError(message="device list, "
                       + rjson['errmsg'])

    adevs = []
    for dev in rjson:
        res = None

        # check the filters
        if apply_list_filters(filters, dev):
            res = {
                'name': dev['hostdev_name'],
            }
            if '_ipadd' in dev:
                res['extracted_ips'] = dev['_ipadd']
            else:  # pragma: no cover
                res['hostdev_ip_formated'] = dev['hostdev_ip_formated']

        # expose metadata if any
        if res and metadatas:
            for _md in metadatas:
                tag = f"tag_hostdev_{_md}"
                if tag in dev and dev[tag] != '':
                    res[_md] = dev[tag]

        if res:
            adevs.append(res)

    return adevs


# ------------------------------------------
def list_devices(sds=None,
                 filters=None,
                 metadatas=None,
                 limit=10):
    """ limit: max number of device to return, 0 for all
        filters: returned device should match all filters
            {'type':'in_subnet', 'val': '10.149.0.0/16'},
            {'type':'of_class', 'val': 'AWS-EC2'},
            {'type':'metadata', 'name': 'cores', 'val': '1'},
            {'type':'space', 'val': 'ex-space-01'},
    """

    offset = 0
    collected = 0
    page = 500
    alldevs = []

    if sds is None:
        raise SDSInitError(message="no sds object in list_devices")

    if filters is None:  # pragma: no cover
        filters = []

    # if no filter on IP address, add one
    ip_filt = False
    for filt in filters:
        if 'type' not in filt:
            raise SDSDeviceError(message="list filter without type")
        if filt['type'] == "in_subnet":
            ip_filt = True

    if not ip_filt:
        filters.append({'type': 'in_subnet', 'val': '0.0.0.0/0'})

    while limit == 0 or collected < limit:
        adevs = list_devices_page(sds,
                                  filters,
                                  metadatas,
                                  offset=offset,
                                  page=page)

        if adevs is None:
            break

        collected += len(adevs)
        alldevs += adevs

        offset += page

    if limit and len(alldevs) > limit:
        alldevs = alldevs[:limit]

    return alldevs
