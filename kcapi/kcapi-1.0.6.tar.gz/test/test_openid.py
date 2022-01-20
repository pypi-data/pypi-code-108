import unittest, time
from rhsso import OpenID, RestURL
from .testbed import TestBed 

WRONG_URL =  'https://sso-wrong-cvaldezr-stage.apps.sandbox-m2.ll9k.p1.openshiftapps.com'

class Testing_OpenID(unittest.TestCase):
    def test_oidc_ctor(self): 
        try:
            OpenID({"client_id":"admin-cli"}, WRONG_URL)
        except Exception as E:
            self.assertEqual("password" in str(E), True)

        try:
            OpenID({"client_id":"admin-cli", "realm": "my_realm", "password": "xxx"}, WRONG_URL)
        except Exception as E:
            self.assertEqual("username" in str(E), True)

        self.assertRaises(Exception, lambda: OpenID({"client_id":"admin-cli"})) 

    def test_oidc_login_on_wrong_url(self):
        oid_client = OpenID({
            "client_id": "admin-cli",
            "username": "6OPtWY33", 
            "password":"I6gglTeDLlmmpLYoAAUMcFQqNOMjw5dA", 
            "grant_type":"password",
            "realm" : "master"
            }, )
        
        self.assertRaises(Exception, lambda: oid_client.getToken()) 

    def test_oidc_login_on_wrong_password(self):
        oid_client = OpenID({
            "client_id": "admin-cli",
            "username": "6OPtWY33", 
            "password":"I6gglTeDLlmmpLYoAAUMcFQqNOMjw5dA", 
            "grant_type":"password",
            "realm" : "master"
            }, self.ENDPOINT)

        try:
            oid_client.getToken()
        except Exception as E:
            self.assertEqual("Unauthorized" in str(E), True)

    def test_creating_oidc_client_using_factory(self):
        oidc = OpenID.createAdminClient(self.USER, self.PASSWORD)
        self.assertIsNotNone( oidc.getToken(self.ENDPOINT) )

    def test_oidc_login(self):
        oid_client = OpenID({
            "client_id": "admin-cli",
            "username": self.testbed.USER, 
            "password": self.testbed.PASSWORD, 
            "grant_type":"password",
            "realm" : "master"
            }, self.ENDPOINT)

        token = oid_client.getToken()
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 1011)
        
    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.kc = self.testbed.getKeycloak()
        self.realm = self.testbed.REALM 
        self.master_realm = self.testbed.getAdminRealm()
        self.ENDPOINT = self.testbed.ENDPOINT
        self.USER = self.testbed.USER
        self.PASSWORD = self.testbed.PASSWORD
        
    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()



if __name__ == '__main__':
    unittest.main()
