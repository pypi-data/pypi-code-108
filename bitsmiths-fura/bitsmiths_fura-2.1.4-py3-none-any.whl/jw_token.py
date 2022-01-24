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

import datetime
import json
import jwcrypto.jwt
import jwcrypto.jwk


class JwToken:
    """
    Abstract api/web token object.

    NOTE, how to generate a new symmetric key:

    > from jwcrypto import jwt, jwk
    > key = jwk.JWK(generate='oct', size=256)
    > key.export()
    """
    MODULE = 'bs_fura.JwToken'
    DT_FMT = '%Y%m%d%H%M%S'

    def __init__(self, tok_key: dict):
        """
        Constructor.

        :param tok_key: (dict) The token key dictionary.
        """
        self._key = jwcrypto.jwk.JWK(**tok_key)


    def new_token(self, timeout: int, claim: dict) -> str:
        """
        Generate a new user token.

        :param timeout: The timeout in minutes of the token, 0 means it does not timeout.
        :param claim: The token claim (data) values
        :return The generated token.
        """
        exp = ''

        if timeout > 0:
            exp = (datetime.datetime.now() + datetime.timedelta(minutes= timeout)).strftime(self.DT_FMT)

        if not claim:
            claim = {}

        claim['tex']  = exp

        return self.gen_token(claim)


    def invalidate_token(self, claim: dict) -> str:
        """
        Invalidates a token.

        :param claim: The claim dictionary, if None, an empty string is returned.
        :return: The invalidated token.
        """
        if not claim:
            return ''

        for key in claim:
            claim[key] = None

        claim['tex'] = datetime.datetime.now().strftime(self.DT_FMT)

        return self.gen_token(claim)


    def refresh_token(self, timeout: int, claim: dict, old_token: str = None) -> str:
        """
        Generates a new user token if the old token requires a refresh.

        :param timeout: The timeout to give the refreshed token.
        :param claim: The claim (values) dictionary, if None an empty string is returned.
        :param oldToken: Optionally pass in old token, it will be used if a new token is not necessary.
        :return (string) The refreshed token.
        """
        if not claim:
            return ''

        if old_token and not claim.get('tex'):
            return old_token

        if timeout < 1:
            return old_token

        claim['tex'] = (datetime.datetime.now() + datetime.timedelta(minutes=timeout)).strftime(self.DT_FMT)

        return self.gen_token(claim)


    def decrypt_token(self, tok: str, ignore_expirey: bool = False) -> dict:
        """
        Decrypts the token back to its claim state.

        :param tok: The encrypted token.
        :param ignore_expirey: If true, ignore the expirey datetime check.
        :return The decrypted claim dictionary.
        """
        etoken = jwcrypto.jwt.JWT(key = self._key, jwt = tok)
        token  = jwcrypto.jwt.JWT(key = self._key, jwt = etoken.claims)
        claim  = json.loads(token.claims)

        if ignore_expirey:
            return claim

        exp = claim.get('tex')

        if exp is None:
            raise xMettle("Claim has missing/invalid expiry.", self.MODULE, xMettle.eCode.TokenInvalid)

        if len(exp):
            try:
                exp = datetime.datetime.strptime(exp, self.DT_FMT)
            except Exception:
                raise xMettle('Claim has missing/invalid expiry', self.MODULE, xMettle.eCode.TokenInvalid)

            dtnow = datetime.datetime.now()

            if exp < dtnow:
                raise xMettle('Access Token Expired @ %s.' % str(exp), self.MODULE, xMettle.eCode.TokenExpired)

        return claim


    def gen_token(self, claim: dict) -> str:
        """
        Generate a new token with the given claim.

        :param claim: The claim dictionary.
        :return The encrypted token.
        """
        token = jwcrypto.jwt.JWT(header={"alg": "HS256"}, claims=claim)
        token.make_signed_token(self._key)

        etoken = jwcrypto.jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=token.serialize())
        etoken.make_encrypted_token(self._key)

        return etoken.serialize()
