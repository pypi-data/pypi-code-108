# encoding=utf-8

import warnings

from hansken.remote import Connection


class Admin(Connection):
    """
    Deprecated, use `hansken.remote.Connection`.
    """
    def __init__(self, base_url_or_connection, keystore_url=None, auth=None, connection_pool_size=None,
                 verify=None):
        if isinstance(base_url_or_connection, Connection):
            connection = base_url_or_connection
            # copy base_url from the connection
            base_url = connection.base_url
            keystore_url = keystore_url or connection.keystore_url
            auth = auth or connection.auth
            # override the arg only if left at None
            verify = connection._session.verify if verify is None else verify
        else:
            base_url = base_url_or_connection
            # True if left at None, otherwise values like True, False or '/path/to/cert' will remain
            verify = verify or verify is None

        super().__init__(base_url, keystore_url=keystore_url, auth=auth,
                         connection_pool_size=connection_pool_size,
                         verify=verify)

        warnings.warn('hansken.admin.Admin has been deprecated, functionality is now available on '
                      'hansken.remote.Connection object', DeprecationWarning)
