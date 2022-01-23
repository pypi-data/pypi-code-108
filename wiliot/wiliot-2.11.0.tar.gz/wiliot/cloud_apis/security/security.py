"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import requests
import pickle
import urllib.parse
from datetime import datetime, timedelta
import base64


class WiliotTokenError(Exception):
    pass


class WiliotAuthentication:
    def __init__(self, base_path, oauth_username, oauth_password):
        self.base_path = base_path
        self.username = oauth_username
        self.password = oauth_password

    def _get_token_from_server(self):
        url = self.base_path + "auth/token?" + urllib.parse.urlencode(
            {"username": self.username, "password": self.password})
        response = requests.post(url)
        try:
            if response.status_code == 200:
                return response.json()
            else:
                raise WiliotTokenError("Failed to get token from server with error code {}".format(response.status_code))
        except Exception as e:
            raise WiliotTokenError("Failed to get token from server with exception: {}".format(e.args[0]))

    def get_token(self):
        # Try to get the token from a file
        try:
            existing_tokens = pickle.load(open("token", "rb"))
        except FileNotFoundError:
            existing_tokens = None
        if existing_tokens is not None:
            if existing_tokens["expires_on"] > datetime.now():
                self.tokens = existing_tokens
                return existing_tokens["access_token"]
            else:
                # The existing token has expired
                # Try to refresh the token
                tokens = self._refresh_token(existing_tokens)
                tokens["expires_on"] = datetime.now() + timedelta(seconds=tokens["expires_in"])
                if tokens and tokens["access_token"]:
                    self.tokens = tokens
                    with open("token", "wb") as f:
                        pickle.dump(tokens, f)
                        f.close()
                    return tokens["access_token"]
        # No existing tokens or unable to refresh the token
        else:
            tokens = self._get_token_from_server()
            # Add an "expires_at" field to reflect the date and this token will expire
            tokens["expires_on"] = datetime.now() + timedelta(seconds=tokens["expires_in"])
            with open("token", "wb") as f:
                pickle.dump(tokens, f)
                f.close()
            return tokens["access_token"]

    def _refresh_token(self, current_token):
        try:
            url = self.base_path + "auth/refresh?refresh_token={}".format(current_token["refresh_token"])
            response = requests.post(url)
            if response.status_code != 200:
                # We failed when trying to use the refresh token - need to get a completely new token
                tokens = self._get_token_from_server()
                return tokens
            else:
                return response.json()
        except KeyError:
            # The current token does not contain a refresh token - get a new token
            tokens = self._get_token_from_server()
            return tokens
