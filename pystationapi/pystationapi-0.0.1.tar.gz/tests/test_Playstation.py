import unittest
import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pystationapi.Playstation import Playstation
class TestPlaystation(unittest.TestCase):
    def test_catalog_with_paginate(self):
        """
        Test the api if answer correctly
        """
        playstation = Playstation()
        prova = json.loads(playstation.to_json_from_category(Playstation.SALES,3))
        print(prova[0]['price'].encode('utf-8'))
        
        
        
        assert(len(prova) == 3)
    def test_catalog_with_paginate(self):
        """
        Test the api if answer correctly
        """
        playstation = Playstation()
        prova = json.loads(playstation.to_json_from_category(Playstation.SALES,3))
        
        
        
        assert(len(prova) == 3)

TestPlaystation().test_catalog_with_paginate()