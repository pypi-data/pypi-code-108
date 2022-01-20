import unittest, time
from kcapi import OpenID, RestURL
from .testbed import TestBed
import json

class Testing_User_API(unittest.TestCase):

    def test_adding_credentials_with_wrong_params(self):
        users = self.testbed.getKeycloak().build('users', self.REALM)
        user_info = {'key': 'username', 'value': 'batman'}
        user_credentials = {'temporary': False, 'passwordWrongParam':'12345'}
        try: 
            state = users.updateCredentials(user_info, user_credentials).isOk()
        except Exception as E:
            self.assertEqual("Missing parameter: value" in str(E), True)


    def test_adding_credentials_to_user(self):

        users = self.testbed.getKeycloak().build('users', self.REALM)
        user_info = {'key': 'username', 'value': 'batman'}
        user_credentials = {'temporary': False, 'value':'12345'}
        state = users.updateCredentials(user_info, user_credentials).isOk()
        self.assertTrue(state)

        oid_client = OpenID({
            "client_id": "dc",
            "username": "batman",
            "password":"12345",
            "grant_type":"password",
            "realm" : self.REALM
            }, self.testbed.ENDPOINT)

        token = oid_client.getToken()
        self.assertNotEqual(token, None)

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.REALM = self.testbed.REALM

    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()

if __name__ == '__main__':
    unittest.main()
