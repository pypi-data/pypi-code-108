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

from bs_fura.db.tables  import tUsrAuth

from .auth       import Auth
from .auth_async import AuthAsync


def get_auth_object(auth_type: str) -> Auth:
    """
    Gets the associated auth type.
    """

    if auth_type == tUsrAuth.AuthType_Couplet.key_password:
        from .auth_password import AuthPassword
        return AuthPassword()

    if auth_type == tUsrAuth.AuthType_Couplet.key_token:
        from .auth_token    import AuthToken
        return AuthToken()

    raise Exception('Auth type [%s] not expected' % auth_type)


async def get_auth_object_async(auth_type: str) -> AuthAsync:
    """
    Gets the associated async auth type.
    """

    if auth_type == tUsrAuth.AuthType_Couplet.key_password:
        from .auth_password_async import AuthPasswordAsync
        return AuthPasswordAsync()

    if auth_type == tUsrAuth.AuthType_Couplet.key_token:
        from .auth_token_async    import AuthTokenAsync
        return AuthTokenAsync()

    raise Exception('Auth type [%s] not expected' % auth_type)
