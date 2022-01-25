# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 12:42:36 alex>
#
# only for python v3

"""
SOLIDserver base object
"""

# import logging

from SOLIDserverRest.Exception import SDSError


__all__ = ["Base"]


# just container class, no need for methods
# pylint: disable=R0903
class Base:
    """ standard class for all objects in SDS """
    # ---------------------------

    def __init__(self, sds=None, name=None):
        """init the base object:
        """

        # if true, modification on object are pushed to SDS
        self.in_sync = False

        self.sds = sds
        self.set_sds(sds)
        self.myid = -1
        self.name = name
        self.set_name(name)
        self.params = {}
        self.additional_params = {}
        self.additional_where_params = {}

    # -------------------------------------
    def clean_params(self):
        """ clean the object params """
        self.in_sync = False
        self.sds = None
        self.myid = -1
        self.name = None
        self.params = {}

    # ---------------------------
    def set_sds(self, sds=None):
        """set the sds connection for this object"""
        self.sds = sds

    # ---------------------------
    def set_name(self, name=None):
        """set the name for this object"""
        if name is None:
            self.name = None
            return

        if isinstance(name, str):
            self.name = name
        else:
            self.name = None
            raise SDSError("name format not valid")

    # ---------------------------
    def set_sync(self):
        """set the object modification sync with SDS"""
        self.in_sync = True

    # ---------------------------
    def set_async(self):
        """set the object modification async with SDS,
           calling update() required"""
        self.in_sync = False

    # ---------------------------
    def __str__(self):
        """return the string notation of the base object"""
        return f" sync: {self.in_sync}"

    # -------------------------------------
    def _get_id_by_name(self, query, key, name, key_id=None):
        """get the ID from its name, return None if non existant"""

        params = {
            "WHERE": f"{key}_name='{name}'",
            "limit": 1,
            **self.additional_params
        }

        # logging.info(self.additional_where_params)
        for _key, _value in self.additional_where_params.items():
            if isinstance(_value, str):
                params['WHERE'] += f" and {_key}='{_value}'"
            elif isinstance(_value, int):
                params['WHERE'] += f" and {_key}={_value}"

        # pylint: disable=E1101
        if hasattr(self, 'space'):
            if self.space:
                params['WHERE'] += f" and site_id={self.space.myid}"

        # specific for networks
        if hasattr(self, 'subnet_addr'):
            if self.subnet_addr:
                params['WHERE'] += " and start_hostaddr="
                params['WHERE'] += f"'{self.subnet_addr}'"

        if hasattr(self, 'parent_network'):
            if self.parent_network:
                params['WHERE'] += " and parent_subnet_id="
                params['WHERE'] += f"'{self.parent_network.myid}'"
            elif 'parent_subnet_id' in self.params:
                if self.params['parent_subnet_id']:
                    _psid = self.params['parent_subnet_id']
                    params['WHERE'] += " and parent_subnet_id="
                    params['WHERE'] += f"'{_psid}'"

        # logging.info(query)
        # logging.info(params)

        try:
            rjson = self.sds.query(query,
                                   params=params)
        except SDSError as err_descr:
            msg = f"cannot found object by name {key}_name={name}"
            msg += " / "+str(err_descr)
            raise SDSError(msg) from err_descr

        if rjson[0]['errno'] != '0':  # pragma: no cover
            raise SDSError("errno raised on get id by name")

        if key_id:
            return rjson[0][f'{key_id}_id']

        return rjson[0][f'{key}_id']

    # -------------------------------------
    def _get_id(self, query, key):
        """get the ID for the current object based
           on its current name
        """

        if self.myid >= 0:
            return self.myid

        if self.params[f'{key}_id'] is None:
            _id = self._get_id_by_name(query=query,
                                       key=key,
                                       name=self.name)

        self.myid = int(_id)

        return self.myid

    # -------------------------------------
    def set_param(self, param=None, value=None, exclude=None, name=None):
        """ set a specific param value """
        if param is None or not isinstance(param, str):
            return

        if value is None:
            return

        if param not in self.params:
            return

        b_do_set = True

        # exclude
        if exclude is not None:
            if param in exclude:
                b_do_set = False

        if b_do_set:
            self.params[param] = value
            if param == name:
                self.name = value

        if self.in_sync:
            self.update()

    # -------------------------------------
    def set_additional_params(self, **kwargs):
        """set any kind of additionnal parameter, may need to filter entries"""
        # if self.additional_params == {}:
        if not self.additional_params:
            self.additional_params = kwargs
        else:
            self.additional_params.update(kwargs)

    # -------------------------------------
    def clean_additional_params(self):
        """clean additionnal parameters on this object"""
        self.additional_params = {}

    # -------------------------------------
    def set_additional_where_params(self, **kwargs):
        """set any kind of additionnal parameter for where queries"""
        # if self.additional_where_params == {}:
        if not self.additional_where_params:
            self.additional_where_params = kwargs
        else:
            self.additional_where_params.update(kwargs)

    # -------------------------------------
    def clean_additional_where_params(self):
        """clean additionnal parameters on this object"""
        self.additional_where_params = {}

    # -------------------------------------
    def update(self):
        """ update template """

    # -------------------------------------
    def str_params(self, exclude=None):
        """ add params value to str"""

        return_val = f" id={self.myid}"

        sep = " "
        for key, value in self.params.items():
            if exclude is not None:
                if key in exclude:
                    continue

            if value == "":
                continue

            return_val += f"{sep}{key}={value}"
            sep = ", "

        return return_val
