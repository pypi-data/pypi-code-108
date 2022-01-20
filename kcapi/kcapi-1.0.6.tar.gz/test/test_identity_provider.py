import unittest, time
from kcapi import OpenID, RestURL
from .testbed import TestBed
import json

def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()
    return file1

class Testing_User_API(unittest.TestCase):

    def test_identity_provider_adding_saml_and_oid_IDP_providers(self):
        idp1 = self.kc.build('identity-provider', self.REALM)
        idp = self.kc.build('idp', self.REALM)
        saml = load_sample('./test/payloads/idp_saml.json')
        oid = load_sample('./test/payloads/idp_oid.json')
        state = idp.create(saml).isOk()
        self.assertTrue(state)
        
        state = idp1.create(oid).isOk()
        self.assertTrue(state)

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.REALM = self.testbed.REALM
        self.kc = self.testbed.getKeycloak()

    @classmethod
    def tearDownClass(self):
        #self.testbed.goodBye()
        return True

if __name__ == '__main__':
    unittest.main()
