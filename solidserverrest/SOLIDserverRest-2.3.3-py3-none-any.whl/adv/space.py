#
# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 11:55:52 alex>
#

"""
SOLIDserver space management

get an existing space:
    space = sdsadv.Space(sds=sds, name="Local")
    space.refresh()

create a new space:
    space = sdsadv.Space(sds, name="test")
    space.create()

"""

import logging
# import math
# import pprint

from SOLIDserverRest.Exception import SDSInitError, SDSError
from SOLIDserverRest.Exception import SDSEmptyError, SDSSpaceError
# from SOLIDserverRest.Exception import SDSNetworkError

from .class_params import ClassParams


class Space(ClassParams):
    """ class to manipulate the SOLIDserver spaces """

    # -------------------------------------
    def __init__(self, sds=None,
                 name="Local",
                 class_params=None):
        """init the space object:
        - sds: object SOLIDserver, could be set afterwards
        - name: space name, default Local
        """

        super().__init__(sds, name)

        # self.name = name
        # self.sds = sds

        self.params = {
            'site_is_template': None,
            'site_id': None,
            'tree_level': None,
            'site_name': None,
            'site_description': None,
            'parent_site_id': None,
            'parent_site_name': None,
            'site_class_name': None,
            'parent_site_class_name': None,
            'row_enabled': None,
            'multistatus': None,
        }

        if class_params is not None:
            self.set_class_params(class_params)

    # -------------------------------------
    def create(self):
        """creates the space in the SDS"""
        if self.sds is None:
            raise SDSSpaceError(message="not connected")

        space_id = None
        try:
            space_id = self._get_id_by_name('ip_site_list', 'site', self.name)
        except SDSError:
            None  # pylint: disable=W0104

        # space_id = self._get_siteid_by_name(self.name)
        if space_id is not None:
            raise SDSSpaceError(message="already existant space")

        params = {
            'site_name': self.name,
            **self.additional_params
        }

        self.prepare_class_params('site', params)

        try:
            rjson = self.sds.query("ip_site_create",
                                   params=params)
        except SDSError:   # pragma: no cover
            logging.error("create space")

        if len(rjson) != 1:   # pragma: no cover
            raise SDSSpaceError(message="space creation error,"
                                + " array not recognized")
        if 'ret_oid' not in rjson[0]:   # pragma: no cover
            raise SDSSpaceError(message="space creation error, id not found")

        self.params['site_id'] = int(rjson[0]['ret_oid'])
        self.refresh()

    # -------------------------------------
    def delete(self):
        """deletes the space in the SDS"""
        if self.sds is None:
            raise SDSSpaceError(message="not connected")

        # space_id = self._get_siteid_by_name(self.name)
        space_id = self._get_id_by_name('ip_site_list', 'site', self.name)

        try:
            rjson = self.sds.query("ip_site_delete",
                                   params={
                                       'site_id': space_id,
                                       **self.additional_params
                                   })
            if 'errmsg' in rjson:  # pragma: no cover
                raise SDSSpaceError(message="space delete error, "
                                    + rjson['errmsg'])
        except SDSError as sdse:   # pragma: no cover
            raise SDSSpaceError(message="space delete error") from sdse

    # -------------------------------------
    def refresh(self):
        """refresh content of the object from the SDS"""
        if self.sds is None:
            raise SDSInitError(message="not connected")

        if self.params['site_id'] is None:
            space_id = self._get_id_by_name('ip_site_list', 'site', self.name)
        else:
            space_id = self.params['site_id']

        if space_id is None:
            raise SDSEmptyError(message="non existant space")

        rjson = self.sds.query("ip_site_info",
                               params={
                                   "site_id": space_id,
                                   **self.additional_params
                               })

        if not rjson:   # pragma: no cover
            raise SDSSpaceError(message="space refresh error, len of array")

        rjson = rjson[0]

        for label in ['site_is_template',
                      'site_id',
                      'tree_level',
                      'site_name',
                      'site_description',
                      'parent_site_id',
                      'parent_site_name',
                      'site_class_name',
                      'parent_site_class_name',
                      'row_enabled',
                      'multistatus']:
            if label not in rjson:   # pragma: no cover
                raise SDSError(f"parameter {label} not found in space")
            self.params[label] = rjson[label]

        self.myid = int(self.params['site_id'])

        if 'site_class_parameters' in rjson:
            self.update_class_params(rjson['site_class_parameters'])

    # -------------------------------------
    # def list_block_networks(self, offset=0, page=25, limit=0, collected=0):
    #     """return the list of blocks"""
    #     params = {
    #         'limit': page,
    #         'offset': offset
    #     }

    #     if limit > 0:
    #         if page > limit:
    #             params['limit'] = limit

    #     params['WHERE'] = "site_id='{}'".format(self.myid)
    #     params['WHERE'] += " and subnet_level='0' and is_terminal='0'"

    #     try:
    #         rjson = self.sds.query("ip_subnet_list",
    #                                params=params)
    #     except SDSEmptyError:
    #         return None

    #     if 'errmsg' in rjson:  # pragma: no cover
    #         raise SDSNetworkError(message="net list, "
    #                               + rjson['errmsg'])

    #     anets = []
    #     for net in rjson:
    #         anets.append({
    #             'start_hostaddr': net['start_hostaddr'],
    #             'subnet_size': 32-int(math.log(int(net['subnet_size']), 2)),
    #             'subnet_name': net['subnet_name']
    #         })

    #     # no limit, we should get all the records
    #     if len(rjson) == page:
    #         if limit == 0 or collected < limit:
    #             newnets = self.list_block_networks(offset+page,
    #                                                page=page,
    #                                                limit=limit,
    #                                                collected=(len(anets)
    #                                                           + collected))
    #             if newnets is not None:
    #                 anets += newnets

    #     if limit and len(anets) > limit:
    #         anets = anets[:limit]

    #     return anets

    # -------------------------------------
    def __str__(self):
        """return the string notation of the space object"""
        return_val = f"*space* name={self.name}"

        if self.myid != -1:
            return_val += f" id={self.myid}"

        if self.params['parent_site_id'] is not None:
            return_val += f" parent={self.params['parent_site_id']}"

        return_val += str(super().__str__())

        return return_val
