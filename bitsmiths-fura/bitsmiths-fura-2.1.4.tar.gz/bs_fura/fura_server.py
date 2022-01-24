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

import json

from mettle.braze.Server  import Server
from mettle.lib.xMettle   import xMettle

from .access       import Access
from .dao          import Dao
from .errcode      import ErrCode
from .fura_token   import FuraToken
from .xfura        import xFura


class FuraServer(Server):
    """
    A standard/sample implementation of a Fura server/service.
    """
    MODULE         = 'bs_fura.FuraServer'
    AUTH_LOGGED_IN = '_LOGGED_IN_'

    def __init__(self, marsh, trans, dao: Dao, ft: FuraToken):
        """
        Standard construtor, but takes a FuraToken object.

        :param marsh: (Marshaler) Braze generates server masharler
        :param trans: (Transport) Braze transport object.
        :param dao: Dao object.
        :param ft: Fura token.
        """
        Server.__init__(self, marsh, trans)

        self._tok        = None
        self._dao        = dao
        self._fura_token = ft


    def token_set(self, tok):
        self._tok = tok


    def token_get(self):
        return '' if not self._tok else self._tok


    def auth(self, rpc_name: str, rpc_auth: str, rpc_args: dict) -> dict:
        self._log.debug('FuraServer.auth - start [rpc:%s, auth:%s]' % (
            rpc_name, rpc_auth))

        if not rpc_auth:
            raise Exception('Authorize has no method! [rpc:%s]' % str(rpc_name))

        if not self._tok:
            raise xMettle("Token has not been set! [rpc:%s, rpc_auth:%s]!" % (
                str(rpc_name), str(rpc_auth)), self.MODULE, xMettle.eCode.TokenInvalid)

        claim = self._fura_token.read_usr_token(self._tok)

        self._dao.dbcon.rollback()

        try:
            with Access(self._dao, claim['site'], claim['usr'], rpc_name) as acc:
                self._tok     = self._fura_token.refresh_token(acc, claim, self._tok)
                claim['role'] = acc._role

                if rpc_auth == self.AUTH_LOGGED_IN:
                    return claim

                acc.required(rpc_auth, rpc_args.get('eatok'))

            self._log.debug('FuraServer.auth - done [success, usrid:%s, rpc:%s, auth:%s]' % (
                str(claim.get('usr')), rpc_name, rpc_auth))

        except xFura as xf:
            self._log.debug('FuraServer.auth - done [failed:%s, usrid:%s, rpc:%s, auth:%s]' % (
                str(xf), str(claim.get('usr')), rpc_name, rpc_auth))

            ec = xf.get_error_code()

            if ec == ErrCode.AccessDenied:
                raise xMettle("Access denied [ec:%d, reason:%s]!" % (ec.value, ec.name),
                              self.MODULE,
                              xMettle.eCode.CredDenied)

        except Exception as x:
            self._log.debug('FuraServer.auth - done [failed:%s, usrid:%s, rpc:%s, auth:%s]' % (
                str(x), str(claim.get('usr')), rpc_name, rpc_auth))
            raise
        finally:
            self._dao.dbcon.commit()

        return claim


    def _init_fura_token(self):
        cfg = self._dao.cfg.load(self._dao, 0, 'token.webkey')

        tokkey = json.load(cfg['token.webkey'])

        return FuraToken(tokkey)
