# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #
import datetime
import os.path

from .base_config import BaseConfig
# from .dao         import Dao


class Config(BaseConfig):
    """
    Class that loads config values on demand from the database. The config values are cached
    for as long as the config is set to.
    """

    def __init__(self):
        """
        Constructor.
        """
        BaseConfig.__init__(self)


    def load(self,
             dao,  # : Dao,
             site_id         : int,
             values          : list,
             expand_env_vars : bool = True,
             must_exist      : bool = True) -> dict:
        """
        Loads config values and caches them.

        :param dao: The Dao object ot use.
        :param site_id: The siteid, 0 for the system config.
        :param values: List of string values to read, if empty assumes namespace is passed.
        :param expand_env_vars: If set to false, won't attempt to expand the env vars.
        :param must_exist: If set to false, won't raise errors if there are missing confg values.
        :return: The site config loaded.
        """
        dtnow = datetime.datetime.now()
        cfg   = self._init_site_config(site_id, dtnow)
        fc    = None

        if type(values) == str:
            values = [values]

        for val in values:
            if val in cfg:
                if must_exist and not cfg[val]:
                    raise Exception('Fura config value not set. [cfg:%s, site_id:%s]' % (val, site_id))
                continue

            if not site_id:
                if fc is None:
                    fc = dao.db_dao.dConfig(dao.pod.dbcon)

                if not fc.try_select_one_deft(val):
                    if must_exist:
                        raise Exception('Fura config value not set. [cfg:%s, site_id:%d]' % (val, site_id))
                    cfg[val] = None
                    continue

                cfg[val] = os.path.expandvars(fc.rec.value) if expand_env_vars else fc.rec.value
            else:
                if fc is None:
                    fc = dao.db_dao.dSiteCfg(dao.pod.dbcon)

                if not fc.try_select_one_deft(site_id, val):
                    if must_exist:
                        raise Exception('Fura site config value not found. [cfg:%s, siteid:%d]' % (
                            val, site_id))
                    cfg[val] = None
                    continue

                cfg[val] = os.path.expandvars(fc.rec.value) if expand_env_vars else fc.rec.value

        return cfg
