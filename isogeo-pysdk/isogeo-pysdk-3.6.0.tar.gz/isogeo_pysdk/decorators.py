# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo Python SDK - Decorators
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
from datetime import datetime
from functools import wraps

# ##############################################################################
# ########## Globals ###############
# ##################################


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiDecorators(object):

    # API Client (Requests [oAuthLib] Session)
    api_client = None

    @classmethod
    def _check_bearer_validity(self, decorated_func):
        """Check API Bearer token validity and refresh it if needed.

        Isogeo ID delivers authentication bearers which are valid during
        a certain time. So this decorator checks the validity of the token
        comparing with actual datetime (UTC) and renews it if necessary.
        See: https://tools.ietf.org/html/rfc6750#section-2

        :param decorated_func token: original function to execute after check
        """

        @wraps(decorated_func)
        def wrapper(*args, **kwargs):
            # compare token expiration date and ask for a new one if it's expired
            if datetime.utcnow() > datetime.utcfromtimestamp(
                self.api_client.token.get("expires_at")
            ):
                self.api_client.refresh_token(
                    token_url=self.api_client.auto_refresh_url
                )
                logging.debug("Token was about to expire, so has been renewed.")
            else:
                logging.debug("Token is still valid.")

            # let continue running the original function
            return decorated_func(*args, **kwargs)

        return wrapper


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    pass
