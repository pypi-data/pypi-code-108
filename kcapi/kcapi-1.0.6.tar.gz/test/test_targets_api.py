import unittest, time
from kcapi.rest.crud import Targets
from kcapi.rest.url import RestURL
import json


TEST_URL = 'https://hello.com'

def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()
    return file1

def exist(that, res, name):
    ret  = res.findFirstByKV('username', name)
    that.assertEqual(name, ret['firstName'], 'We expect a role ['+name+'] to be created')
    return ret['id']


class Testing_User_API(unittest.TestCase):

    
    def testing_targets_class(self):
        target = Targets()
        target.makeWithURL(TEST_URL)
        

    def testing_targets_class_with_wrong_method(self):
        target = Targets.makeWithURL(TEST_URL)
        
        try:
            target.url('wrong') 
        except Exception as E:
            self.assertEqual(str(E), 'Method: wrong not supported')

    def testing_add_resources(self):
        target = Targets.makeWithURL(TEST_URL)
        target.addResourcesFor('create', ['bye']) 
        self.assertEqual('https://hello.com/bye', str(target.url('create')))
        self.assertEqual('https://hello.com', str(target.url('delete')))
        self.assertEqual('https://hello.com', str(target.url('read')))


    def testing_targets_copy_method(self):
        target = Targets.makeWithURL(TEST_URL)
        t2 = target.copy()

        t2.addResourcesFor('create', ['bye']) 
        self.assertNotEqual(str(t2.url('create')), t2.url('create'))
        self.assertEqual('https://hello.com/bye', str(t2.url('create')))
        self.assertEqual('https://hello.com', str(target.url('create')))



    def testing_targets_remove_last_method(self):
        target = Targets.makeWithURL(TEST_URL)
        target.addResourcesFor('create', ['bye']) 
        target.removeLast() 
        self.assertEqual('https://hello.com', str(target.url('create')))
        self.assertEqual('https://hello.com', str(target.url('delete')))
        self.assertEqual('https://hello.com', str(target.url('read')))

    def testing_targets_change_method(self):
        target = Targets.makeWithURL(TEST_URL)
        target.addResources(['bye']) 
        target.change('hello') 

        self.assertEqual('https://hello.com/hello', str(target.url('create')))
        self.assertEqual('https://hello.com/hello', str(target.url('delete')))
        self.assertEqual('https://hello.com/hello', str(target.url('read')))


    def testing_remove_resources_method(self):
        target = Targets.makeWithURL(TEST_URL)
        target.addResources(['1','2','hh','bye']) 
        target.removeResources(['1', '2', 'hh'])

        self.assertEqual('https://hello.com/bye', str(target.url('create')))
        self.assertEqual('https://hello.com/bye', str(target.url('read')))
        self.assertEqual('https://hello.com/bye', str(target.url('delete')))
        self.assertEqual('https://hello.com/bye', str(target.url('update')))


    def testing_replace_resources_for_method(self):
        target = Targets.makeWithURL(TEST_URL)
        target.addResources(['1','2','hh','bye']) 
        target.removeResources(['1', '2', 'hh'])

        self.assertEqual('https://hello.com/bye', str(target.url('create')))
        self.assertEqual('https://hello.com/bye', str(target.url('read')))
        self.assertEqual('https://hello.com/bye', str(target.url('delete')))
        self.assertEqual('https://hello.com/bye', str(target.url('update')))





        
            
if __name__ == '__main__':
    unittest.main()
