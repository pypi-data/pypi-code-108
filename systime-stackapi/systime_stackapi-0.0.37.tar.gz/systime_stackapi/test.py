import unittest
import requests
from os import getenv

# to run
# python -m unittest

from systime_stackapi.stackDiscovery import StackDiscovery
from systime_stackapi.backupService import BackupService
from systime_stackapi.stackService import StackService

class TestStringMethods(unittest.TestCase):

    def test_Discovery(self):
        # There are a few different ways to get information out of StackDiscovery.
        # Simply put, the class wraps the output of 
        #   nslookup -q=SRV _stackservice_._tcp.systime.dk
        # in a way that can be used downstream.
        # It is NOT checked, that the stack endpoints actually respond.
        discovery_domain = 'systime.dk'
        discovery = StackDiscovery(domain=discovery_domain)
        stack_list = discovery.stack_list()
        stacks = discovery.discover_stacks()
        self.assertTrue(len(stack_list) > 0)
        for stack_url in stack_list:
            endpoint = discovery.get_stack_endpoint(stack_url)
            self.assertTrue(endpoint is not None)
            r = requests.get('{}/health'.format(endpoint),)
            self.assertTrue(r.status_code == 200)
        self.assertTrue(discovery.stacks.keys() == stack_list)
        self.assertTrue(stacks[0].keys() == stack_list)
        self.assertTrue(stacks[0] == discovery.stacks)

    def test_BackupService(self):
        self.assertTrue(getenv('SYSTIME_STACK_CLI_KEY_NAME'), 'python-opsserver')
        self.assertTrue(getenv('SYSTIME_STACK_CLI_KEY') is not None)
        backup_endpoint = 'https://backup-service.api.systime.dk'
        backup_service = BackupService(backup_endpoint, getenv('SYSTIME_STACK_CLI_KEY_NAME'), getenv('SYSTIME_STACK_CLI_KEY'))
        signed_upload_link = backup_service.create_signed_upload_links('AUTO_CLEANUP', 'TYPO3_INSTALLATION', 'dummy')
        self.assertTrue(signed_upload_link is not None)
        #backups = backup_service.list_backups('AUTO_CLEANUP', 'TYPO3_INSTALLATION')
        #self.assertTrue(backups is not None)
        #self.assertTrue(len(backups) > 0)
        #signed_download_link = backup_service.get_signed_download_links('AUTO_CLEANUP', 
        #                                                                'TYPO3_INSTALLATION', 
        #                                                                backups[0].get('InstallationName'),
        #                                                                backups[0].get('BackupId'))
        #self.assertTrue(signed_download_link is not None)

    def test_StackService(self):
        discovery_domain = 'systime.dk'
        discovery = StackDiscovery(domain=discovery_domain)
        stack_list = discovery.stack_list()
        stacks = discovery.discover_stacks()
        for stack_url in stack_list:
            endpoint = discovery.get_stack_endpoint(stack_url)
            service = StackService(endpoint, getenv('SYSTIME_STACK_CLI_KEY_NAME'), getenv('SYSTIME_STACK_CLI_KEY'))
            installations = service.installations_list()
            self.assertTrue(installations is not None)





    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
