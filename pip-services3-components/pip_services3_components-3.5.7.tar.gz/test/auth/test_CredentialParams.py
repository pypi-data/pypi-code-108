# -*- coding: utf-8 -*-
"""
    tests.auth.test_CredentialParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_components.auth.CredentialParams import CredentialParams

class TestCredentialParams:

    def test_store_key(self):
        credential = CredentialParams(self)
        credential.set_store_key(None)
        assert None == credential.get_store_key()
        
        credential.set_store_key("Store key")
        assert "Store key" == credential.get_store_key()
        assert True == credential.use_credential_store()

    def test_username(self):
        credential = CredentialParams(self)
        credential.set_username(None)
        assert None == credential.get_username()
        
        credential.set_username("Kate Negrienko")
        assert "Kate Negrienko" == credential.get_username()

    def test_password(self):
        credential = CredentialParams(self)
        credential.set_password(None)
        assert None == credential.get_password()
        
        credential.set_password("qwerty")
        assert "qwerty" == credential.get_password()

    def test_access_key(self):
        credential = CredentialParams(self)
        credential.set_access_key(None)
        assert None == credential.get_access_key()
        
        credential.set_access_key("key")
        assert "key" == credential.get_access_key()
