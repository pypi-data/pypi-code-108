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

import bcrypt
import re

from mettle.lib import xMettle

from .auth import Auth

from bs_fura.db.tables import tUsrAuth


class AuthPassword(Auth):
    """
    Password authenticator object.
    """
    SALT_ROUNDS  = 12

    def __init__(self):
        """
        Constructor.
        """
        Auth.__init__(self)


    def auth_type(self) -> str:
        """
        Overload base method.
        """
        return tUsrAuth.AuthType_Couplet.key_password


    def _auth_data_for_save(self, data: str, salt: str) -> str:
        """
        Overload base method.
        """
        pwdstr = '%d%s%s' % (self._site_id, self._usr_id, data)
        bpwd   = bytes(pwdstr, 'utf8')
        hashed = bcrypt.hashpw(bpwd, bcrypt.gensalt(rounds=self.SALT_ROUNDS))

        return str(hashed, 'utf8')


    def _auth_data_for_compare(self, data: str, au_rec: tUsrAuth) -> bool:
        """
        Overload base method.
        """
        pwdstr = '%d%s%s' % (self._site_id, self._usr_id, data)
        bpwd   = bytes(pwdstr, 'utf8')
        hashed = str(bcrypt.hashpw(bpwd, bytes(au_rec.auth_data, 'utf8')), 'utf8')

        return hashed == au_rec.auth_data


    def _auth_data_ok(self, data: str):
        """
        Overload, ensure password matches the password policy.

        :param data: The password.
        """
        pol   = self.get_auth_policy()

        if not pol.get('regex'):
            return

        regex = re.compile(pol['regex'])

        if not regex.fullmatch(data):
            raise xMettle('Password policy failed. %s' % (pol['descr']))
