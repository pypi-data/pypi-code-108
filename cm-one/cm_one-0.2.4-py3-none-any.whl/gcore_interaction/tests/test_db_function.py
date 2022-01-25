import unittest
from gravity_interface.gcore_interaction import db_functions as db_funcs


class DbFuncsTester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.general_tables_dict = {'trash_cats':
                                        {'ТКО':
                                             {'id': 13,
                                              'cat_name': 'ТКО'}},
                                    'trash_types':
                                        {'КГО':
                                             {'id': 7,
                                              'name': 'КГО',
                                              'category': 13}}}

    def test_id_getter(self):
        tableinfo = {'trash_cats': {'ТКО': {'id':13,}}}
        response = db_funcs.get_id_by_repr_table(tableinfo, 'trash_cats', 'ТКО')
        self.assertEqual(response, 13)

    def test_tc_id_getter_by_repr(self):
        response = db_funcs.get_trashtypes_by_trashcat_repr(self.general_tables_dict, 'trash_types', 'trash_cats', 'ТКО')
        self.assertEqual(response, ['КГО'])

    def test_get_repr_by_id_table(self):
        response = db_funcs.get_repr_by_id_table(self.general_tables_dict, 'trash_cats', 13)
        self.assertEqual(response, 'ТКО')


if __name__ == '__main__':
    unittest.main()