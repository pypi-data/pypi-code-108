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


class BaseConfig:
    """
    Class that loads config values on demand from the database. The config values are cached
    for as long as the config is set to.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.cache_time = 60  # min
        self.cache      = {}


    def _init_site_config(self, site_id: int, dtnow: datetime.datetime) -> dict:
        """
        Initialize and return a site config if required.

        :param site_id: (int) The site id.
        :param dtnow: (datetime) Current datetime.
        :return: The config.
        """
        cfg = self.cache.get(site_id)

        if cfg is None:
            cfg = {}
            self.cache[site_id] = cfg

        if cfg.get('__cache__') is None or dtnow > cfg['__cache__']:
            cfg.clear()
            cfg['__cache__'] = dtnow + datetime.timedelta(minutes=self.cache_time)

        return cfg
