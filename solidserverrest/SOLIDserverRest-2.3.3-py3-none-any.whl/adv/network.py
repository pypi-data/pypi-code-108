# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 13:51:41 alex>
#
# pylint: disable=R0801


"""
SOLIDserver network manager

"""

# pylint: disable=too-many-branches

import math

from packaging.version import Version, parse
from SOLIDserverRest.Exception import (SDSEmptyError, SDSError,
                                       SDSNetworkError,
                                       SDSNetworkNotFoundError)

from .class_params import ClassParams
from .space import Space

# import logging
# import pprint


# pylint: disable=R0902
class Network(ClassParams):
    """ class to manipulate the SOLIDserver network """

    # -------------------------------------
    def __init__(self, sds=None,  # pylint: disable=too-many-arguments
                 space=None,
                 name=None,
                 class_params=None):
        """init a network object:
        - sds: object SOLIDserver, could be set afterwards
        - space: space object for this network
        - name: name of the subnet
        """

        super().__init__(sds, name)

        # params mapping the object in SDS
        self.clean_params()

        # reset the name since suppressed by the clean proc
        self.name = name

        self.set_sds(sds)
        # self.set_name(name)

        self.description = None

        if space and not isinstance(space, Space):
            raise SDSNetworkError("no valid space provided")
        self.space = space

        self.subnet_addr = None
        self.subnet_prefix = None
        self.is_block = False
        self.is_terminal = False
        self.parent_network = None

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def clean_params(self):
        """ clean the object params """

        super().clean_params()

        self.subnet_addr = None
        self.subnet_prefix = None

        self.is_block = False
        self.is_terminal = False

        self.parent_network = None

        self.params = {
            'subnet_id': None,
            'parent_subnet_id': None
        }

    # -------------------------------------
    def set_address_prefix(self, ipaddress, prefix):
        """set the address and prefix of this network"""
        # need to normalize and check the ip address
        self.subnet_addr = ipaddress
        self.subnet_prefix = prefix

        if self.in_sync:  # pragma: no cover
            self.update()

    # -------------------------------------
    def set_is_block(self, block=False):
        """is this network a block"""
        self.is_block = block
        if block:
            self.set_is_terminal(False)

        if self.in_sync:  # pragma: no cover
            self.update()

    # -------------------------------------
    def set_is_terminal(self, terminal=False):
        """is this network a terminal"""
        self.is_terminal = terminal
        if terminal:
            self.set_is_block(False)

        if self.in_sync:  # pragma: no cover
            self.update()

    # -------------------------------------
    def set_parent(self, network):
        """set the parent network => not a block then"""
        if network.myid == -1:
            raise SDSNetworkError("no valid parent network found")

        self.parent_network = network
        self.set_is_block(False)

        if self.in_sync:  # pragma: no cover
            self.update()

    # -------------------------------------
    def set_param(self, param=None, value=None, exclude=None, name=None):
        """ set a specific param on the network object """
        if param == 'description':
            self.description = str(value)
            self.set_class_params({'__eip_description': self.description})
            return

        super().set_param(param,
                          value,
                          exclude=['subnet_id'],
                          name='subnet_name')

    # -------------------------------------
    def find_free(self, prefix, max_find=4):
        """ find the next free subnets in the space within this network
            by order of priority to avoid fragmentation
        """
        params = {
            'site_id': self.space.params['site_id'],
            'prefix': prefix,
            'max_find': max_find,
            'begin_addr': self.subnet_addr,
            **self.additional_params
        }

        params['WHERE'] = f'block_id={self.myid}'

        try:
            rjson = self.sds.query("ip_subnet_find_free",
                                   params=params)
        except SDSEmptyError:
            return None

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSNetworkError(message="find free net, " +
                                  rjson['errmsg'])

        aip = []
        for net in rjson:
            iphex = net['start_ip_addr']
            ipv4_addr = "{}.{}.{}.{}".format(int(iphex[0:2], 16),
                                             int(iphex[2:4], 16),
                                             int(iphex[4:6], 16),
                                             int(iphex[6:8], 16))
            aip.append(ipv4_addr)

        return aip

    # -------------------------------------
    def find_free_ip(self, max_find=4):
        """ find the next free ip in the current subnet
        """
        params = {
            'max_find': max_find,
            'subnet_id': self.myid,
            **self.additional_params
        }

        try:
            rjson = self.sds.query("ip_address_find_free",
                                   params=params)
        except SDSEmptyError:
            return None

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSNetworkError(message="find free ip, " +
                                  rjson['errmsg'])

        aip = []
        for net in rjson:
            aip.append(net['hostaddr'])

        return aip

    # -------------------------------------
    def get_subnet_list(self,    # pylint: disable=too-many-arguments
                        depth=1,  # only one level
                        terminal=None,
                        offset=0,
                        page=25,
                        limit=50,
                        collected=0):
        """return the list of subnet in the parent subnet"""
        params = {
            'limit': page,
            'offset': offset,
            'ORDERBY': 'start_ip_addr',
            ** self.additional_params,
        }

        if limit > 0:
            if page > limit:
                params['limit'] = limit

        if 'WHERE' not in params:
            params['WHERE'] = ""
        else:
            params['WHERE'] += " and "

        params['WHERE'] += f"site_id='{self.space.params['site_id']}'"

        # look only under the block
        params['WHERE'] += f" and subnet_path like '%#{self.myid}#%'"

        if depth == 1:
            params['WHERE'] += f"and parent_subnet_id='{self.myid}'"

        if terminal is not None:
            if terminal in [1, 0]:
                params['WHERE'] += f" and is_terminal='{terminal}'"

        try:
            rjson = self.sds.query("ip_subnet_list",
                                   params=params)
        except SDSEmptyError:
            return None

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSNetworkError(message="net list, " +
                                  rjson['errmsg'])

        anets = []
        for net in rjson:
            anets.append({
                'start_hostaddr': net['start_hostaddr'],
                'subnet_size': 32 - int(math.log(int(net['subnet_size']), 2)),
                'subnet_name': net['subnet_name']
            })

        # no limit, we should get all the records
        if len(rjson) == page:
            if limit == 0 or collected < limit:
                newnets = self.get_subnet_list(depth, terminal,
                                               offset + page,
                                               page=page,
                                               limit=limit,
                                               collected=(len(anets) +
                                                          collected))
                if newnets is not None:
                    anets += newnets

        if limit and len(anets) > limit:
            anets = anets[:limit]

        return anets

    # -------------------------------------
    def create(self):
        """ create the subnet in SDS """

        if self.sds is None:
            raise SDSNetworkError(message="not connected")

        if self.space is None:
            raise SDSNetworkError("no space attached to network for create")

        if self.subnet_addr is None:
            raise SDSNetworkError("no address on network for create")

        if self.subnet_prefix is None:
            raise SDSNetworkError("no address size on network for create")

        # if object already created
        if self.myid > 0:
            return

        params = {
            'subnet_addr': self.subnet_addr,
            'subnet_prefix': self.subnet_prefix,
            'subnet_name': self.name,
            'site_id': self.space.params['site_id'],
            **self.additional_params
        }

        if self.is_block:
            params['is_terminal'] = '0'
            params['subnet_level'] = '0'
        else:
            if self.parent_network is not None:
                params['parent_subnet_id'] = self.parent_network.myid
            else:  # pragma: no cover
                assert None, "TODO - not a block and no parent set, abort"

            if self.is_terminal:
                params['is_terminal'] = '1'
            else:
                params['is_terminal'] = '0'

        self.prepare_class_params('network', params)

        rjson = self.sds.query("ip_subnet_create",
                               params=params)

        if 'errmsg' in rjson:
            raise SDSNetworkError(message="creation, " +
                                  rjson['errmsg'])

        self.params['subnet_id'] = int(rjson[0]['ret_oid'])
        self.myid = int(self.params['subnet_id'])

        self.refresh()

    # -------------------------------------
    def update(self):
        """ update the network in SDS """

        if self.sds is None:
            raise SDSNetworkError(message="not connected")

        params = {
            'subnet_id': self._get_id(query="ip_subnet_list",
                                      key="subnet"),
            'subnet_name': self.name,
            **self.additional_params
        }

        self.prepare_class_params('network', params)

        # logging.info(params)

        rjson = self.sds.query("ip_subnet_update",
                               params=params)

        if 'errmsg' in rjson:  # pragma: no cover
            raise SDSNetworkError(message="network update error, " +
                                  rjson['errmsg'])

        self.refresh()

    # -------------------------------------
    def delete(self):
        """deletes the network in the SDS"""
        if self.sds is None:
            raise SDSNetworkError(message="not connected")

        if self.params['subnet_id'] is None:
            raise SDSNetworkNotFoundError("on delete")

        params = {
            'subnet_id': self.params['subnet_id'],
            **self.additional_params
        }

        self.sds.query("ip_subnet_delete",
                       params=params)

        self.clean_params()

    # -------------------------------------
    def refresh(self):
        """refresh content of the network from the SDS"""

        if self.sds is None:
            raise SDSNetworkError(message="not connected")

        try:
            subnet_id = self._get_id(query="ip_subnet_list",
                                     key="subnet")
        except SDSError as err_descr:
            msg = "cannot get network id"
            msg += " / " + str(err_descr)
            raise SDSNetworkError(msg) from err_descr

        params = {
            "subnet_id": subnet_id,
            **self.additional_params
        }

        try:
            rjson = self.sds.query("ip_subnet_info",
                                   params=params)
        except SDSError as err_descr:
            msg = f"cannot get network info on id={subnet_id}"
            msg += " / " + str(err_descr)
            raise SDSNetworkError(msg) from err_descr

        rjson = rjson[0]
        # logging.info(rjson)

        labels = ['subnet_id',
                  'subnet_name',
                  'subnet_size',
                  'subnet_level',
                  'parent_subnet_id',
                  'is_terminal',
                  'subnet_allocated_size',
                  'subnet_allocated_percent',
                  'subnet_used_size',
                  'subnet_used_percent',
                  'subnet_ip_used_size',
                  'subnet_ip_used_percent',
                  'subnet_ip_free_size',
                  'is_in_orphan',
                  'lock_network_broadcast',
                  'tree_level']
        if parse(self.sds.get_version()) >= Version("7.0.0"):
            labels.extend(['start_hostaddr', 'end_hostaddr'])

        for label in labels:
            if label not in rjson:  # pragma: no cover
                msg = f"parameter {label} not found in network"
                raise SDSNetworkError(msg)
            self.params[label] = rjson[label]

        self.myid = int(rjson['subnet_id'])
        if rjson['is_terminal'] == '1':
            self.is_terminal = True
        else:
            self.is_terminal = False
            if rjson['subnet_level'] == '0':
                self.is_block = True
            else:
                self.is_block = False

        if 'start_hostaddr' in rjson:
            self.subnet_addr = rjson['start_hostaddr']

        # should be this variable (see API doc), but not working...
        if 'network_class_parameters' in rjson:   # pragma: no cover
            self.update_class_params(rjson['network_class_parameters'])

        if 'subnet_class_parameters' in rjson:
            self.update_class_params(rjson['subnet_class_parameters'])

        descr = self.get_class_params('__eip_description')
        if descr is not None:
            self.description = descr

    # -------------------------------------
    def __str__(self):  # pragma: no cover
        """return the string notation of the network object"""

        return_val = f"*network* name={self.name}"

        if self.description is not None:
            return_val += f" \"{self.description}\""

        if self.is_block:
            return_val += " [block]"

        if self.is_terminal:
            return_val += " [terminal]"
        else:
            return_val += " [network]"

        return_val += self.str_params(exclude=['subnet_id',
                                               'subnet_name'])

        if self.parent_network:
            return_val += f" parent={self.parent_network.myid}"

        return_val += str(super().__str__())

        return return_val
