"""
The authenticator code that is used on the JupyterHub for authenticating people by the entries in a database.
"""

import requests
from jupyterhub.auth import Authenticator
from tornado import gen
from traitlets import Unicode, Bool


# noinspection PyUnresolvedReferences
class CouchDBAuthenticator(Authenticator):
    """
    All code needs to be recycled
    """

    couchdb_url = Unicode(
        help='URL to visit the CouchDB server',
        config=True
    )

    couchdb_username = Unicode(
        help='username to log into the CouchDB server',
        config=True
    )

    couchdb_password = Unicode(
        help='password to log into the CouchDB server',
        config=True
    )

    ssl_verification = Bool(
        help='switch off ssl verification to support self-signed certificates in development environments',
        config=True
    )

    # pylint: disable=invalid-overridden-method
    @gen.coroutine
    def authenticate(self, _, data):
        username = data['username']
        provided_password = data['password']

        # Query CouchDB
        search_url = f"https://{self.couchdb_url}/users/_find"
        query = {
            "selector": {
                "username": username,
                "active": True
            },
            "fields": ["username", "password"]
        }
        response = requests.post(
            search_url,
            json=query,
            auth=requests.auth.HTTPBasicAuth(self.couchdb_username, self.couchdb_password),
            verify=self.ssl_verification
        )

        try:
            response.raise_for_status()  # raise exception for HTTP error codes
        except requests.HTTPError as exception:
            self.log.error(exception, exc_info=True)
            return

        parsed_response = response.json()
        if not hasattr(parsed_response, "keys") or "docs" not in parsed_response.keys():
            self.log.error(f"Malformed response of CouchDB search query: '{response.text}' "
                           f"with status code '{response.status_code}'")
            return

        if len(parsed_response["docs"]) == 0:
            self.log.debug(f"Provided user name '{username}' not existent")
            return
        if len(parsed_response["docs"]) > 1:
            self.log.warning(f"For the username '{username}' duplicate entries exist in the database, please tidy up!")
            return
        retrieved_user = parsed_response["docs"][0]
        actual_password = retrieved_user["password"]
        if actual_password != provided_password:
            self.log.debug(f"Provided password of '{username}' did not match")
            return

        self.log.debug(f"User '{username}' logged in")
        return username
