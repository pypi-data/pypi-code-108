import unittest, time
from rhsso import OpenID, KeycloakAdmin, discover, RestURL

sso = OpenID({
        "client_id": "admin-cli",
        "username": "admin", 
        "password":"admin1234", 
        "grant_type":"password",
        "realm" : "master"
        })

test_url = "https://sso-cvaldezr-dev.apps.sandbox.x8i5.p1.openshiftapps.com"

class TestingSSOAPI(unittest.TestCase):

    def testing_discovery_url(self):
        json_resp = discover(test_url, "master")
        self.assertNotEqual(json_resp, None)

     
    def test_login(self):
        token = sso.getToken(test_url)
        self.assertNotEqual(token, None)

    def testing_passing_non_openid_url(self):
        self.assertRaises(Exception, lambda: sso.getToken("https://www.google.com")) 

    def testing_CRUD_api(self):
        admin = self.admin

        realm = admin.master()
        self.assertNotEqual(realm.getHeaders(), None)

        state = realm.create({"enabled": "true", "id": "my_realm_1", "realm": "my_realm_1"})
        self.assertEqual(state, True)

        obj = realm.findById("my_realm_1")
        self.assertEqual(obj['id'], 'my_realm_1')

        obj['displayName'] = "MyRealm"
        state_update = realm.update("my_realm_1", obj)
        self.assertEqual(state_update, True)

        updated_object = realm.findById("my_realm_1")
        self.assertEqual(updated_object['displayName'], "MyRealm")

        remove_state = realm.remove("my_realm_1")
        self.assertEqual(remove_state, True)


    def testing_building_your_own_URL(self):
       my_url =  RestURL("https://sso-cvaldezr-dev.apps.sandbox.x8i5.p1.openshiftapps.com/auth/admin")
       my_url.addResources(['realms'])
       realms = self.admin.buildForURL(my_url)
       realms_list = realms.findAll()

       self.assertEqual(realms_list.status_code, 200)
       self.assertGreater(len(realms_list.json()), 1)

    def testing_graceful_handling_of_incorrect_credentials(self):
       kc = KeycloakAdmin({
            "username": "bad_user", 
            "password": "bad_password"
            }, test_url)

       realm = admin.master()

       state = realm.create({"enabled": "true", "id": "my_realm_1", "realm": "my_realm_1"})
       self.assertNotEqual(state, True)

    @classmethod
    def setUpClass(self):
        self.test_realm = "realm_for_testing"
        self.admin = KeycloakAdmin({
            "username": "6OPtWY33", 
            "password": "I6gglTeDLlmmpLYoAAUMcFQqNOMjw5dA"
            }, test_url)

        self.master_realm = self.admin.master()
        self.master_realm.create({"enabled": "true", "id": self.test_realm, "realm": self.test_realm})

        time.sleep(1)

     

    @classmethod
    def tearDownClass(self):
        realm = self.admin.master()
        remove_state = self.master_realm.remove(self.test_realm)
        

if __name__ == '__main__':
    unittest.main()
