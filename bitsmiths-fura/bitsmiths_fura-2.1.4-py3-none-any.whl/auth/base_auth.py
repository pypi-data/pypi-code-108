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

import random
import string

from bs_fura.dao       import Dao
from bs_fura.dao_async import DaoAsync

from bs_fura.db.tables  import tUsrAuth


class BaseAuth:
    """
    Base authorize object.
    """
    RESET_TOKEN_EMAIL_LEN = 32
    SALT_LEN              = 32
    MAX_FAIL_CNT          = 5


    def __init__(self):
        """
        Constructor.
        """
        self._dao     = None
        self._site_id = None
        self._usr_id  = None
        self._au_rec  = None


    def __del__(self):
        """
        Destructor.
        """
        self._au_rec = None


    def __enter__(self):
        """
        On enter event.
        """
        return self


    def is_token_based(self) -> bool:
        """
        Virtual method to check if this is a token based authentication
        method or not.

        :return: True if auth is token based.
        """
        return False


    def initialize(self, dao: "Dao|DaoAsync", site_id: int, usr_id: str):
        """
        Initialize method.

        :param dao: Data access object.
        :param site_id: The site id.
        :param usr_id: The user id.
        """
        self._dao     = dao
        self._site_id = site_id
        self._usr_id  = usr_id


    def auth_type(self) -> str:
        """
        Get the auth type id.

        :return: The tUsrAuth.auth_type_Couplet key.
        """
        raise Exception('Abstract method not implemented.')


    def auth_type_name(self):
        """
        Get the auth type name

        :return: The tUsrAuth.AuthType_Couplet key.
        """
        return tUsrAuth.AuthType_Couplet.get_value(self.auth_type())


    def _auth_data_for_save(self, data: str, salt: str) -> str:
        """
        Manipulate the authdata for saving, comparing. This method is
        called before saving the auth data.

        :param data: The auth data as the user sent it in.
        :param salt: The salt for the auth data.
        :return: The auth data to be saved.
        """
        return data


    def _auth_salt_for_save(self, data) -> str:
        """
        Creates the auth salt for saving.

        :param data: The data input, usually the password.
        :return: The salt string.
        """
        return ''.join(random.SystemRandom().choice(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits) for _ in range(self.SALT_LEN))


    def _auth_data_for_compare(self, data: str, au_rec: tUsrAuth) -> bool:
        """
        Convert the users auth data into a compariable format to
        ensure the data is valid.

        :param data: The auth data the user sent in.
        :param au_rec: The auth data from the database.
        :return: True if the input data matches the auth rec.
        """
        return False
