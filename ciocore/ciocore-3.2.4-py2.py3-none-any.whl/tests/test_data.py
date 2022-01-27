""" test data

   isort:skip_file
"""
import json
import os
import sys
import unittest
from mock import patch
from ciocore import data

PROJECTS = [
    "Deadpool",
    "Harry Potter & the chamber of secrets",
    "Captain Corelli's Mandolin",
    "Gone with the Wind"
]

INSTANCE_TYPES = [
    {
        "cores": 8,
        "memory": 30.0,
        "description": "8 core, 30GB Mem",
        "name": "n1-standard-8"
    },
    {
        "cores": 64,
        "memory": 416.0,
        "description": "64 core, 416GB Mem",
        "name": "n1-highmem-64"
    },
    {
        "cores": 4,
        "memory": 26.0,
        "description": "4 core, 26GB Mem",
        "name": "n1-highmem-4"
    },
    {
        "cores": 32,
        "memory": 208.0,
        "description": "32 core, 208GB Mem",
        "name": "n1-highmem-32"
    }
]

with open(os.path.join(os.path.dirname(__file__), "fixtures", "sw_packages.json"), 'r') as content:
    SOFTWARE = json.load(content)["data"]


class TestDataSingleton(unittest.TestCase):
 
 
    def setUp(self):
        projects_patcher = patch('ciocore.api_client.request_projects', return_value=PROJECTS)
        instance_types_patcher = patch('ciocore.api_client.request_instance_types', return_value=INSTANCE_TYPES)
        software_packages_patcher = patch('ciocore.api_client.request_software_packages', return_value=SOFTWARE)
        self.mock_projects = projects_patcher.start()
        self.mock_instance_types = instance_types_patcher.start()
        self.mock_software_packages = software_packages_patcher.start()

        self.addCleanup(projects_patcher.stop)
        self.addCleanup(instance_types_patcher.stop)
        self.addCleanup(software_packages_patcher.stop)
        data.__data__ = {}
        data.__product__ = None

    def test_init_sets_project_global(self):
        data.init("all")
        self.assertEqual(data.product(), "all") 

    def test_init_raises_if_product_falsy(self):
        with self.assertRaises(ValueError):
            data.init()
        with self.assertRaises(ValueError):
            data.init("")

    def test_data_raises_if_not_initialized(self):
        with self.assertRaises(ValueError):
            data.data()

    def test_valid(self):
        self.assertEqual(data.valid(), False) 
        data.init("all")
        data.data()
        self.assertEqual(data.valid(), True) 

    def test_clear(self):
        data.init("all")
        data.data()
        self.assertEqual(data.valid(), True) 
        data.clear()
        self.assertEqual(data.valid(), False) 

    def test_does_not_refresh_if_not_force(self):
        data.init("all")
        p1 = data.data()["projects"]
        self.assertEqual(len(p1), 4) 
        self.mock_projects.return_value =  ["a", "b"]
        p2 = data.data()["projects"]
        self.assertEqual(p2, p1) 


    def test_does_refresh_if_force_all(self):
        data.init("all")
        p1 = data.data()["projects"]
        self.assertEqual(len(p1), 4) 
        self.mock_projects.return_value =  ["a", "b"]
        p2 = data.data(force=True)["projects"]
        self.assertNotEqual(p2, p1) 
        self.assertEqual(len(p2), 2) 
        

    def test_does_refresh_projects_if_force_projects(self):
        data.init("all")
        p1 = data.data()["projects"]
        self.assertEqual(len(p1), 4) 
        self.mock_projects.return_value =  ["a", "b"]
        p2 = data.data(force_projects=True)["projects"]
        self.assertNotEqual(p2, p1) 
        self.assertEqual(len(p2), 2) 
        

    def test_does_not_refresh_inst_types_if_force_projects(self):
        data.init("all")
        p1 = data.data()["instance_types"]
        self.assertEqual(len(p1), 4) 
        self.mock_instance_types.return_value =  INSTANCE_TYPES[1:3]
        p2 = data.data(force_projects=True)["instance_types"]
        self.assertEqual(p2, p1) 
        self.assertEqual(len(p2), 4) 
