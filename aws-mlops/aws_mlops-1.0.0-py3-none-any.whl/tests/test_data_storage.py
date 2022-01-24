import unittest
import os
import json
import pandas as pd
import tests.config as config
from aws_mlops.data_storage import DataStorage

class s3fs_for_testing():
    tmp = None
    def __init__(self, *args, **kwargs):
        self.tmp = os.path.dirname(os.path.realpath(__file__))

    def open(self, s3_url, mode='rb'):
        filename = os.path.basename(s3_url)
        path = os.path.join(self.tmp, filename)
        return open(path, mode)

class TestService(unittest.TestCase, DataStorage):
    ds = None
    tmp = None

    def __init__(self, *args, **kwargs):
        self.ds = DataStorage()
        self.ds.s3 = s3fs_for_testing()
        self.tmp = os.path.dirname(os.path.realpath(__file__))
        unittest.TestCase.__init__(self, *args, **kwargs)
        
    def test_checkpoint_and_restore(self):
        data = {'col_1': [0, 1, 2, 3], 'col_2': ['a', 'b', 'c', 'd']}
        df_prepared = pd.DataFrame.from_dict(data)
        df_prepared.index.rename('index', inplace=True)

        self.ds.checkpoint(df_prepared)
        df_restored = self.ds.restore()
        df_restored.set_index('index', inplace=True)

        df_diff = pd.concat([df_prepared, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

    def test_local_save_and_read(self):
        data = {'col_1': [0, 1, 2, 3], 'col_2': ['a', 'b', 'c', 'd']}
        df_prepared = pd.DataFrame.from_dict(data)
        df_prepared.index.rename('index', inplace=True)

        self.ds.local_save(df_prepared, self.tmp)
        df_restored = self.ds.local_read(self.tmp)
        df_restored.set_index('index', inplace=True)

        df_diff = pd.concat([df_prepared, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

    def test_create_dataframe_from_dict(self):
        fh = open(self.tmp + '/config.json')
        json_config = json.load(fh)
        fh.close()

        df_created = self.ds.create_dataframe_from_dict(json_config)
        self.assertTrue('service' in df_created)
        self.assertTrue('container_input.container.version' in df_created)
        self.assertTrue('last_output.container_input.container.version' in df_created)

        df_created = self.ds.create_dataframe_from_dict(json_config, ['container_input', 'service'])
        self.assertFalse('service' in df_created)
        self.assertFalse('container_input.container.version' in df_created)
        self.assertTrue('last_output.container_input.container.version' in df_created)

        df_created = self.ds.create_dataframe_from_dict(json_config, ['last_output', 'service'])
        self.assertFalse('service' in df_created)
        self.assertTrue('container_input.container.version' in df_created)
        self.assertFalse('last_output.container_input.container.version' in df_created)

    def test_create_dataframe_from_py(self):
        df_created = self.ds.create_dataframe_from_py(config)
        df_created_columns = df_created.columns.to_list()
        self.ds.local_save(df_created, self.tmp, 'config.csv', True)
        df_restored = self.ds.local_read(self.tmp, 'config.csv')
        self.assertTrue(df_created_columns.sort() == df_restored.columns.to_list().sort())
        self.assertTrue('service' in df_restored)
        self.assertTrue('container_input.version' in df_restored)

        black_list = ['version', 'os', 'git', 'datetime', 'definitions_config', 'get_git_details', 'create_ts', 'slash_to_dash']
        df_created_columns_without_black_list = list(set(df_created_columns) - set(black_list))
        df_created = self.ds.create_dataframe_from_py(config, black_list)
        self.assertTrue(df_created_columns_without_black_list.sort() == df_created.columns.to_list().sort())
        self.assertTrue('service' in df_created)
        self.assertTrue('container_input.version' in df_created)

        black_list = ['service', 'container_input', 'os', 'git', 'datetime', 'definitions_config', 'get_git_details', 'create_ts', 'slash_to_dash']
        df_created_columns_without_black_list = list(set(df_created_columns) - set(black_list))
        df_created = self.ds.create_dataframe_from_py(config, black_list)
        self.assertTrue(df_created_columns_without_black_list.sort() == df_restored.columns.to_list().sort())
        self.assertFalse('service' in df_created)
        self.assertFalse('container_input.version' in df_created)

    def test_save_and_restore_test(self):
        data = {'target': [0, 1, 2, 3], 'identifier': ['a', 'b', 'c', 'd'], 'col_3': ['f', 's', 't', 'f']}
        df_prepared = pd.DataFrame.from_dict(data)

        df_test = self.ds.save_test(df_prepared)
        self.ds.local_save(df_test, self.tmp, 'test.csv', header=False)
        [columns_names, target, identifier] = self.ds.restore_test()
        self.assertEqual(columns_names['list_columns'][0], 'col_3')

        # first row preserved
        df_test_restored = pd.read_csv(os.path.join(self.tmp, 'test.csv'), names=list(columns_names['list_columns']))
        df_merged = pd.concat([target, identifier, df_test_restored], axis=1)
        self.assertEqual(df_merged['target'][0], 0)
        self.assertEqual(df_merged['identifier'][0], 'a')
        self.assertEqual(df_merged['col_3'][0], 'f')

        # first row overwritten
        df_test_restored = self.ds.local_read(self.tmp, 'test.csv')
        columns = ['target', 'identifier'] + list(columns_names['list_columns'])
        df_merged = pd.concat([target, identifier, df_test_restored], axis=1)
        df_merged.columns = columns
        self.assertEqual(df_merged['target'][0], 0)
        self.assertEqual(df_merged['identifier'][0], 'a')
        self.assertEqual(df_merged['col_3'][0], 's')

    def test_convert_dtypes(self):
        data = {'i': [0, 1, 2, 3], 'f': [0.1, 0.2, 0.3, 0.4], 'b': [True, False, True, False],
                'is': ['0', '1', '2', '3'], 'fs': ['0.1', '0.2', '0.3', '0.4'], 'bs': ['True', 'False', 'True', 'False']}
        df_prepared = pd.DataFrame.from_dict(data)
        dtypes = {'is':'int', 'fs':'float', 'bs':'bool'}
        self.assertEqual(df_prepared['i'].dtypes, 'int')
        self.assertEqual(df_prepared['f'].dtypes, 'float64')
        self.assertEqual(df_prepared['b'].dtypes, 'bool')
        self.assertEqual(df_prepared['is'].sum(), '0123')
        self.assertEqual(df_prepared['fs'].sum(), '0.10.20.30.4')
        self.assertTrue(df_prepared['bs'][0])
        self.assertTrue(df_prepared['bs'][1])
        df_converted = self.ds.convert_dtypes(dtypes, df_prepared)
        self.assertEqual(df_converted['i'].sum(), df_prepared['i'].sum())
        self.assertEqual(df_converted['f'].sum(), df_prepared['f'].sum())
        self.assertEqual(df_converted['b'][0], df_prepared['b'][0])
        self.assertEqual(df_converted['b'][1], df_prepared['b'][1])
        self.assertEqual(df_converted['is'].sum(), df_prepared['i'].sum())
        self.assertEqual(df_converted['fs'].sum(), df_prepared['f'].sum())
        self.assertEqual(df_converted['bs'][0], df_prepared['b'][0])
        self.assertEqual(df_converted['bs'][1], df_prepared['b'][1])

if __name__ == '__main__':
    unittest.main()