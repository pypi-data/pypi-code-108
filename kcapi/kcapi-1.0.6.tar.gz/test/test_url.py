import unittest, time
from kcapi import RestURL 

class Testing_URL_API(unittest.TestCase):

    def testing_only_setting_hostname(self): 
        try:
            my_url = RestURL('my-host')
        except Exception as E:
            self.assertEqual("schema" in str(E), True)


        my_url = RestURL('https://my-host')
        self.assertEqual('https://my-host', str(my_url))
        _url = my_url.copy()
        self.assertEqual('https://my-host', str(_url))

    def testing_obj_construction(self):
        self.assertRaises(Exception, lambda: RestURL()) 
        nurl = RestURL(self.endpoint)
        self.assertEqual(str(nurl), self.endpoint)

    def testing_adding_resources(self):
        url = self.url.copy()
        url.addResource("auth", "admin")
        test1 = self.endpoint + "/auth/admin"
        test2 = self.endpoint + "/auth/admin/realms/AAA/client-templates/my_client/scope-mappings/clients/123"
        test3 = self.endpoint + "/auth/admin/realms/AAA/client-templates/my_client_1/scope-mappings/clients/542"

        self.assertEqual(str(url), test1)
        url.addResource("realms", "AAA")

        t1 = url.copy()
        t2 = url.copy()

        t1.addResource("client-templates", "my_client")
        t2.addResource("client-templates", "my_client_1")

        t1.addResource("scope-mappings", "clients")
        t2.addResource("scope-mappings", "clients")

        t1.addResource("clients", "123")
        t2.addResource("clients", "542")

        self.assertEqual(str(t1), test2)
        self.assertEqual(str(t2), test3)

    def testing_single_entry_resources(self):
        url = self.url.copy()

        url.addResources([])
        self.assertEqual(str(url), self.endpoint)

        url.addResources(["auth"])
        self.assertEqual(str(url), self.endpoint + "/auth")
    
    def testing_multiple_entries(self):
        url = self.url.copy()
        raw_str = "/auth/admin/realms/aaa/client-templates/my_client/scope-mappings/clients/123"
        test = raw_str.split("/")
        test =  list( filter(lambda n: n != "", test) )
        url.addResources(test)
        self.assertEqual(str(url), self.endpoint + raw_str)


    def testing_resource_replacement(self):
        url = self.url.copy()
        raw_str = "/auth/admin/realms/aaa/roles"
        test = raw_str.split("/")
        test =  list( filter(lambda n: n != "", test) )
        url.addResources(test)
        self.assertEqual(str(url), self.endpoint + raw_str)

        url.replaceResource('roles', 'roles-by-id')
        self.assertEqual(str(url), self.endpoint + "/auth/admin/realms/aaa/roles-by-id")


    def testing_getting_actual_resource(self):
        self.assertEqual(self.url.getCurrentResource(), "resource1")

    def testing_getting_target(self):
        self.assertEqual(self.url.target(), "https://my-sso.com")

    def testing_replace_current_resource_target(self):
        url = self.url.copy()
        url.replaceCurrentResourceTarget('resource-new')
        self.assertEqual(str(url), "https://my-sso.com/resource-new")


    def testing_removing_resources(self):
        url = "https://my-sso.com"
        myURL = self.url.copy()
        myURL.removeResources(["resource1", "res2"])
        self.assertEqual(str(myURL), url)

    def testing_adding_none_values_to_resources(self):
        urlString = "https://my-sso.com"
        url = RestURL(urlString)
        url.addResource(None, None)
        url.addResources([None, None, None])

        self.assertEqual(urlString, str(url))

        url.addResources([None, None, None, "id", "5"])
        self.assertEqual("https://my-sso.com/id/5", str(url))

    def testing_with_ipv4_host(self):
        url = "http://192.168.1.100:8080/"
        myURL = RestURL(url)
        self.assertEqual(str(myURL), url[:-1])

    def testing_remove_last(self):
        urlString = "https://my-sso.com/a/b/c"
        url = RestURL(urlString)
        url.removeLast()
        self.assertEqual(str(url), "https://my-sso.com/a/b")

    @classmethod
    def setUpClass(self):
        self.endpoint = "https://my-sso.com/resource1"
        self.url = RestURL(self.endpoint)

if __name__ == '__main__':
    unittest.main()
