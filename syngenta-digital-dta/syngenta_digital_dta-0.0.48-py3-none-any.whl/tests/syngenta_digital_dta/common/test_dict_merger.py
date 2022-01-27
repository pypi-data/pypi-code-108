import unittest

from syngenta_digital_dta.common import dict_merger


class DictMergerTest(unittest.TestCase):

    def test_merge(self):
        old_dict = {
            'key1': 'value1'
        }
        new_dict = {
            'key2': 'value2'
        }
        results = dict_merger.merge(old_dict, new_dict)
        self.assertDictEqual(results, {
            'key1': 'value1',
            'key2': 'value2'
        })

    def test_merge_remove_key(self):
        old_dict = {
            'key1': 'value1'
        }
        new_dict = {
            'key2': 'value2'
        }
        results = dict_merger.merge(old_dict, new_dict, update_dict_operation='remove')
        self.assertDictEqual(results, old_dict)

    def test_merge_remove_array(self):
        old_dict_list = {
            'list1': [0,1,2]
        }
        new_dict_list = {
            'list1': [0,1]
        }
        results = dict_merger.merge(old_dict_list, new_dict_list, update_dict_operation='remove')
        self.assertDictEqual(results, old_dict_list)

    def test_merge_replace_array(self):
        old_dict_list = {
            'list1': [0,1,2,3,4]
        }
        new_dict_list = {
            'list1': [0,1]
        }
        results = dict_merger.merge(old_dict_list, new_dict_list, update_dict_operation='replace')
        self.assertDictEqual(results, old_dict_list)
