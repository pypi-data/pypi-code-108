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

from .auth import Auth

from bs_fura.db.tables  import tUsrAuth


class AuthToken(Auth):
    """
    Token authenticator object, not the password is store in the salt. The
    calling system must bcrypt the hash of "[sitecode] [user_id] [password]"
    """
    TOKEN_LENGTH = 64

    def __init__(self):
        """
        Constructor.
        """
        Auth.__init__(self)


    def auth_type(self):
        """
        Overload base method.
        """
        return tUsrAuth.AuthType_Couplet.key_token


    def is_token_based(self):
        """
        Overload base method.
        """
        return True


    def _auth_data_for_save(self, data: str, salt: str):
        """
        Overload base method.
        """
        tok = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits) for _ in range(self.TOKEN_LENGTH))

        return tok


    def _auth_data_for_compare(self, data: str, au_rec: tUsrAuth):
        """
        Overload base method.
        """
        return data == au_rec.auth_data


    def _auth_data_ok(self, data: str):
        """
        Overload, ensure password matches the password policy.

        :param data: The password.
        """
        pass
