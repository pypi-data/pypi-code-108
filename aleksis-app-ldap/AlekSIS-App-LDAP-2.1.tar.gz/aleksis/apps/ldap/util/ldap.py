"""Extension utilities for django-auth-ldap."""

import logging

logger = logging.getLogger(__name__)


class TemporaryBind:
    """LDAP conection from an LDAPUser object temporarily bound with other credentials."""

    def __init__(self, ldap_user, bind_dn, password):
        self.ldap_user = ldap_user
        self.bind_dn = bind_dn
        self.password = password

    def __enter__(self):
        if self.bind_dn is not None:
            # Bind with defined credentials and mark connection bound
            logger.info("Temporarily binding to LDAP as %s", self.bind_dn)
            self.ldap_user._bind_as(self.bind_dn, self.password, sticky=True)
        return self.ldap_user.connection

    def __exit__(self, type_, value, traceback):
        if self.bind_dn is not None:
            # Re-bind with regular credentials
            # so we do not leak connections with elevated privileges
            logger.info("Ending temporary LDAP bind as %s", self.bind_dn)
            self.ldap_user._bind()
