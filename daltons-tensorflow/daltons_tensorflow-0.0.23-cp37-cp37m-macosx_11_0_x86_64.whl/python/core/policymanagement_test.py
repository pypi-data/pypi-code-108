import unittest
import subprocess
import os 
import socket
import time
import tempfile

from daltons_tensorflow.python.core.policymanagement import PolicyManagementClient

def get_free_ports():
    s1 = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s1.bind(('localhost', 0))
    address, port1 = s1.getsockname()

    s2 = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s2.bind(('localhost', 0))
    address, port2 = s2.getsockname()
        
    s1.close()
    s2.close()
    return port1, port2

grpc_port, http_port = get_free_ports()

example_policy = '''
models:
- id: rand
  type: random
'''

daltons_status, response = subprocess.getstatusoutput('which daltons')

class TestPolicyManagementClient(unittest.TestCase):
    def setUp(self):
        if daltons_status != 0:
            self.skipTest('daltons cmd not found skipping test')    

    @classmethod
    def setUpClass(self):
        if daltons_status != 0:
            return

        self._temp_dir = tempfile.TemporaryDirectory()

        os.mkdir(self._temp_dir.name + '/example')
        with open(self._temp_dir.name + '/example/config.yaml', 'w') as file:
            file.write(example_policy)

        self._process = subprocess.Popen([
            'daltons', 
            'admin', 
            '-g=:{}'.format(grpc_port), 
            '-p=:{}'.format(http_port), 
            '-s=file://{}/'.format(self._temp_dir.name)
        ])
        time.sleep(1)

        self._client = PolicyManagementClient('localhost:{}'.format(grpc_port))

    @classmethod
    def tearDownClass(self):
        if daltons_status != 0:
            return

        self._process.kill()
        self._temp_dir.cleanup()
    
    def test_list_policies(self):
        policies = self._client.list_policies()

        self.assertEqual(policies[0]['id'], 'example')
        self.assertEqual(policies[0]['models'][0]['id'], 'rand')
        self.assertEqual(policies[0]['models'][0]['type'], 'random')

    def test_get_policy(self):
        policy = self._client.get_policy('example')

        self.assertEqual(policy['id'], 'example')
        self.assertEqual(policy['models'][0]['id'], 'rand')
        self.assertEqual(policy['models'][0]['type'], 'random')

    def test_create_policy(self):
        self._client.create_policy({'id': 'foobar'})
        policy = self._client.get_policy('foobar')
        self.assertEqual(policy['id'], 'foobar')

    def test_update_policy(self):
        policy = self._client.get_policy('foobar')
        policy['models'] = [
            {
                'id': 'rand', 
                'type': 'random'
            }
        ]

        self._client.update_policy(policy)
        policy = self._client.get_policy('foobar')
        
        self.assertEqual(policy['id'], 'foobar')
        self.assertEqual(policy['models'][0]['id'], 'rand')
        self.assertEqual(policy['models'][0]['type'], 'random')

    def test_upload_model(self):
        # Lets upload the policy directory as a model ;)
        self._client.upload_model('example', 'rand', 123, self._temp_dir.name + '/example')

        with open('{}/example/rand/{}/config.yaml'.format(self._temp_dir.name, 123), 'r') as f:
            self.assertEqual(f.read(), example_policy)
