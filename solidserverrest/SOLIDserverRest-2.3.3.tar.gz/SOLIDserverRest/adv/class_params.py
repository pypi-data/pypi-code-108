# -*- Mode: Python; python-indent-offset: 4 -*-
#
# Time-stamp: <2022-01-14 12:23:05 alex>
#
# only for python v3

"""
SOLIDserver base object with class parameters
"""

import base64
import urllib
import logging

from .base import Base

__all__ = ["ClassParams"]


class ClassParams(Base):
    """ standard class for all objects in SDS with class parameters """
    # ---------------------------

    def __init__(self, sds=None, name=None):
        """init the object:
        """
        super().__init__(sds, name)

        self.fct_url_encode = urllib.parse.urlencode
        self.fct_b64_encode = base64.b64encode

        self.dclasses = {}
        self.__class_params = {}

        self.class_name = None

    # ---------------------------
    @classmethod
    def decode_class_params(cls, params, val):
        """push decoded parameters in the params structure"""
        if val == "":
            return None

        dir_val = urllib.parse.parse_qsl(val)

        params.update(dir_val)

        # specific
        if 'domain_list' in params:
            dlist = str.split(params['domain_list'], ';')
            params['domain_list'] = dlist

        return True

    # ---------------------------
    @classmethod
    def encode_class_params(cls, params):
        """get parameters from the structure and create string"""

        if not isinstance(params, dict):
            return None

        return urllib.parse.urlencode(params)

    # ---------------------------
    def get_class_params(self, key=None):
        """ get all/one class param """
        if key is None:
            return self.__class_params

        if not isinstance(key, str):
            logging.warning("get_class_params only accepting string as key")
            return None

        if key in self.__class_params:
            return self.__class_params[key]

        return None

    # ---------------------------
    def set_class_params(self, params=None):
        """ set the class param """
        if params is None:
            return None

        if not isinstance(params, dict):
            logging.warning("set class params only support dictionary")
            return None

        self.__class_params = params

        return True

    # ---------------------------
    def add_class_params(self, params=None):
        """ update the class param by adding this part """
        if params is None:
            return None

        if not isinstance(params, dict):
            logging.warning("update class params only support dictionary")
            return None

        self.__class_params.update(params)
        # logging.info(self.__class_params)

        return True

    # ---------------------------
    def prepare_class_params(self, keyprefix=None, params=None):
        """ encode the params into the string and update the dictionary """
        if keyprefix is None:
            return None

        if self.class_name:
            key = f"{keyprefix}_class_name"
            params[key] = self.class_name

        if params is None:
            return None

        if not isinstance(params, dict):
            return None

        if self.__class_params == {}:
            return None

        key = f"{keyprefix}_class_parameters"
        params[key] = self.encode_class_params(self.__class_params)

        # logging.info(params)

        return True

    # ---------------------------
    def update_class_params(self, params=None):
        """ update from a refresh """

        if params is None:
            return None

        if params == "":
            return None

        if isinstance(params, str):
            self.decode_class_params(self.__class_params,
                                     params)
            return True

        if isinstance(params, dict):
            self.__class_params.update(params)

        return True

    # -------------------------------------
    def set_class_name(self, name):
        """ set the class name for the object """
        self.class_name = name

    # -------------------------------------
    def __str__(self):  # pragma: no cover
        if self.__class_params == {}:
            return ""

        return_val = " cparams=["

        sep = ""
        for key, value in sorted(self.__class_params.items()):
            return_val += f"{sep}{key}={value}"
            sep = ", "

        return_val += "]"

        return_val += str(super().__str__())

        return return_val
