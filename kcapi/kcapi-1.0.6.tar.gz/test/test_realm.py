import unittest, time
from kcapi import OpenID, RestURL
from .testbed import TestBed
import json

class Testing_Realm_API(unittest.TestCase):

    def testing_realm_api_methods(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)
        self.assertTrue(hasattr(realms, 'caches'))


    def testing_realm_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearRealmCache().resp().status_code, 204)

    def testing_user_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearUserCache().resp().status_code, 204)


    def testing_key_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearKeyCache().resp().status_code, 204)


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
