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

from mettle.lib import xMettle

from .base_access import BaseAccess
from .jw_token    import JwToken


class FuraToken(JwToken):
    """
    Abstract fura specific api/web token.
    """
    MODULE = "bs_fura.FuraToken"

    def __init__(self, tok_key: dict):
        """
        Constructor.

        :param tokKey: The token key dictionary.
        """
        JwToken.__init__(self, tok_key)


    def new_usr_token(self, acc: BaseAccess, add_claim: dict = None) -> str:
        """
        Generate a new user token.

        :param acc: User access object.
        :param add_claims: Additional claim values.
        :return The generated token.
        """
        return self.new_token(acc._role.sess_timeout, {
                                'site': acc._site.id,
                                'usr': acc._usr_id })



    def read_usr_token(self, tok: str) -> dict:
        """
        Reads the claims of a user token and returns the dicitonary.  Raises an exception if
        the token has expired.

        :param tok: The encrypted token.
        :return: The claim dictionary.
        """
        claim = self.decrypt_token(tok)

        if not claim.get('site'):
            raise xMettle('Token closed.', self.MODULE, xMettle.eCode.TokenExpired)

        if not claim.get('usr'):
            raise xMettle("Claim has missing/invalid user.", self.MODULE, xMettle.eCode.TokenInvalid)

        return claim
