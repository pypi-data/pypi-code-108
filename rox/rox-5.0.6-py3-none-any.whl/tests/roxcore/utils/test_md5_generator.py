import unittest
import hashlib
import json

from rox.core.utils.md5_generator import generate
from rox.core.consts import property_type

class Md5GeneratorTests(unittest.TestCase):

    def hash(self, str):
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest().upper()

    def test_will_check_MD5_uses_right_props(self):
        props = { property_type.PLATFORM.name: 'value' }
        md5 = generate(props, [ property_type.PLATFORM ])
        md5Manual = self.hash('value'.encode('utf-8'))
        self.assertEqual(md5, md5Manual)
    
    def test_will_check_MD5_not_ysing_all_props(self):
        props = { 
            property_type.DEV_MODE_SECRET.name: 'dev',
            property_type.PLATFORM.name: 'value'
        }

        md5 = generate(props, [ property_type.PLATFORM ])
        md5Manual = self.hash('value'.encode('utf-8'))
        self.assertEqual(md5, md5Manual)

    
    def test_will_check_MD5_with_map(self):
        props = { 
            property_type.DEV_MODE_SECRET.name: {"a":22},
            property_type.PLATFORM.name: 'value'
        }
        
        md5 = generate(props, [ property_type.PLATFORM, property_type.DEV_MODE_SECRET ])

        md5Manual = self.hash('value|{\'a\': 22}'.encode('utf-8'))
        self.assertEqual(md5, md5Manual)
