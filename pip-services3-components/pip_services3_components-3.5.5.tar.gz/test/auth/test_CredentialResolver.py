# -*- coding: utf-8 -*-
"""
    tests.auth.test_CredentialResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References

from pip_services3_components.auth.CredentialResolver import CredentialResolver

RestConfig = ConfigParams.from_tuples(
    "credential.username", "Negrienko",
    "credential.password", "qwerty",
    "credential.access_key", "key",
    "credential.store_key", "store key"
)

class TestCredentialResolver:

    def test_configure(self):
        credential_resolver = CredentialResolver(RestConfig)
        config_list = credential_resolver.get_all()
        assert "Negrienko" == config_list[0]["username"]
        assert "qwerty" == config_list[0]["password"]
        assert "key" == config_list[0]["access_key"]
        assert "store key" == config_list[0]["store_key"]

    def test_lookup(self):
        credential_resolver = CredentialResolver()
        credential = credential_resolver.lookup("correlation_id")
        assert None == credential
        
        RestConfigWithoutStoreKey = ConfigParams.from_tuples(
            "credential.username", "Negrienko",
            "credential.password", "qwerty",
            "credential.access_key", "key"
        )
        credential_resolver = CredentialResolver(RestConfigWithoutStoreKey)
        credential = credential_resolver.lookup("correlation_id")
        assert "Negrienko"  == credential.get("username")
        assert "qwerty" == credential.get("password")
        assert "key" == credential.get("access_key")
        assert None == credential.get("store_key")
        
        credential_resolver = CredentialResolver(RestConfig)
        credential = credential_resolver.lookup("correlation_id")
        assert None == credential
        
        credential_resolver.set_references(References())
        try:
            credential = credential_resolver.lookup("correlation_id")
        except Exception as ex:
            assert "Cannot locate reference: Credential store wasn't found to make lookup" == ex.message

