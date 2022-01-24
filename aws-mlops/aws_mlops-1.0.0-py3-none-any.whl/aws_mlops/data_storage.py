"""The class for managing your data

The class accepts two properties:
    'bucket' (string): the bucket name where to save or restore the data
    'key' (string): the path where to save or restore the data

These properties are mandatory. Here's an example:

    >>> from aws_mlops.data_storage import DataStorage
    >>> ds = DataStorage('your-bucket-name', 'key/of/your/files/without/filename')
    >>> ds.checkpoint(my_dataframe)
    >>> my_dataframe = ds.restore()
    >>> ds.save_test(test, [target_column, identifier_column])
    >>> [test, columns, target, identifier] = ds.restore_test([target_column, identifier_column])
    >>> ds.restore_test([target_column, identifier_column])

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-mlops for details
"""
import pandas as pd
import s3fs
import os
from types import ModuleType

class DataStorage():
    s3_url = None
    s3 = None
    def __init__(self, bucket='', key=''):
        self.s3_url = f's3://{bucket}/{key}'
        self.s3 = s3fs.S3FileSystem(anon=False)
    def checkpoint(self, dataframe, filename='temporary.csv', s3_url=None):
        """
        saves your dataframe: when you study how to prep the data,
        you may need to stop all but to save where you arrived
            Arguments:
                dataframe (pandas.DataFrame): dataframe that you want to save
                filename (string): filename that you want to save in s3_url, default is temporary.csv
                s3_url (string): s3 url without filename, default is used that you have passed at the init
        """
        self.save_on_s3(dataframe, filename, s3_url)
    def read(self, fh, header='infer', index_col=None, low_memory=True):
        """
        reads your csv into a dataframe
            Arguments:
                fh (str or file handle): path or object where read your dataframe
                header (str, int, list of int): row number(s) to use as the column names, and the start of the data, default infer
                index_col (int, str, sequence of int / str, or False): column(s) to use as the row labels of the DataFrame, default None
                low_memory (bool): internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference, default with mixed type inference
            Returns:
                pandas.DataFrame
        """
        return pd.read_csv(fh, header=header, index_col=index_col, low_memory=low_memory)
    def local_read(self, path='/opt/ml/processing/input', filename='raw_data.csv', header='infer', index_col=None, low_memory=True):
        """
        reads your csv into a dataframe
            Arguments:
                path (str): path where save your dataframe, default /opt/ml/processing/input
                filename (str): name of file where save your dataframe, default raw_data.csv
                header (str, int, list of int): row number(s) to use as the column names, and the start of the data, default infer
                index_col (int, str, sequence of int / str, or False): column(s) to use as the row labels of the DataFrame, default None
                low_memory (bool): internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference, default with mixed type inference
            Returns:
                pandas.DataFrame
        """
        return self.read(os.path.join(path, filename), header, index_col, low_memory)
    def restore(self, filename='temporary.csv', s3_url=None, header='infer', index_col=None, low_memory=True):
        """
        restores your dataframe
            Arguments:
                filename (string): filename that you have saved in s3_url
                s3_url (string): s3 url without filename, default is used that you have passed at the init
            Returns:
                pandas.DataFrame without header
        """
        if s3_url is None:
            s3_url = self.s3_url
        print('Reading data from {}/{} {} header, {} index column and {} low_memory'.format(s3_url, filename, 'without' if header is None else 'with', 'without' if index_col is [None, False] else 'with', 'without' if low_memory is False else 'with'))
        with self.s3.open(f'{s3_url}/{filename}') as fs:
            return self.read(fs, header, index_col, low_memory)
    def save(self, dataframe, path=None, header=False, index=False):
        """
        converts your dataframe into csv format, default in string without header and index
            Arguments:
                dataframe (pandas.DataFrame): dataframe that you want to convert
                path (str or file handle): path or object where save your dataframe, default None
                header (bool): formats with or without header, default without
                index (bool): formats with or without index, default without
            Returns:
                dataframe converted into csv format or nothing
        """
        if not dataframe.empty:
            return dataframe.to_csv(path, header=header, index=index)#.encode()
        return
    def local_save(self, dataframe, path='/opt/ml/processing/train', filename='train.csv', header=True, index=False):
        """
        converts your dataframe into csv format, default in string without header and index
            Arguments:
                dataframe (pandas.DataFrame): dataframe that you want to convert
                path (str): path where save your dataframe, default /opt/ml/processing/train
                filename (str): name of file where save your dataframe, default train.csv
                header (bool): formats with or without header, default without
                index (bool): formats with or without index, default without
            Returns:
                dataframe converted into csv format or nothing
        """
        print('Saving data to {}'.format(path + '/' + filename))
        self.save(dataframe, os.path.join(path, filename), header=header, index=index)
    def save_on_s3(self, dataframe, filename, s3_url=None, header=True, index=True):
        """
        saves your dataframe into s3
            Arguments:
                dataframe (pandas.DataFrame): dataframe that you want to save
                filename (string): filename that you want to save in s3_url
                s3_url (string): s3 url without filename, default is used that you have passed at the init
        """
        if s3_url is None:
            s3_url = self.s3_url
        print(f'Saving data to {s3_url}/{filename}')
        with self.s3.open(f'{s3_url}/{filename}','wb') as fs:
            self.save(dataframe, fs, header=header, index=index)
    def create_dataframe(self, data, columns_names):
        """
        creates dataframe from config module
            Arguments:
                data (dict): dictionary
                columns_names (list of str): list of columns names
            Returns:
                pandas.DataFrame
        """
        columns = []
        for column in columns_names:
            if isinstance(data, ModuleType):
                columns.append(pd.json_normalize({column: getattr(data, column)}))
            else:
                columns.append(pd.json_normalize({column: data[column]}))
        dataframe = pd.concat(columns, axis=1)
        return dataframe
    def create_dataframe_from_dict(self, dict, black_list = []):
        """
        creates dataframe from config module
            Arguments:
                dict (dict): dictionary
                black_list (list of str): attributes that you want to exclude into dataframe
            Returns:
                pandas.DataFrame
        """
        columns_names = [item for item in dict.keys() if not item in (black_list)]
        return self.create_dataframe(dict, columns_names)
    def create_dataframe_from_py(self, config, black_list = []):
        """
        creates dataframe from config module
            Arguments:
                config (object): config module imported
                black_list (list of str): attributes that you want to exclude into dataframe
            Returns:
                pandas.DataFrame
        """
        if isinstance(config, ModuleType):
            return self.create_dataframe_from_dict(config.dictionary_from_module(config), black_list)
        columns_names = [item for item in dir(config) if not item.startswith("__") and not item in (black_list)]
        return self.create_dataframe(config, columns_names)
    def save_test(self, test, columns=['target', 'identifier'], s3_url=None):
        """
        saves test data: test, columns name without those in columns
            Arguments:
                train (pandas.DataFrame): data for training
                test (pandas.DataFrame): data for testing
                columns (list of string): list of column names
                s3_url (string): s3 url without filename, default is used that you have passed at the init
        """
        if s3_url is None:
            s3_url = self.s3_url
        # save a file for each column in columns
        for column in columns:
            self.save_on_s3(test[column], f'{column}.csv', s3_url, header=True, index=False)
            test.drop([column], axis=1, inplace=True)
        # columns names
        columns_names = pd.DataFrame({"list_columns":test.columns})
        self.save_on_s3(columns_names, 'columns_names.csv', s3_url, header=True, index=False)
        return test
    def restore_test(self, columns=['target', 'identifier'], s3_url=None):
        """
        restores test data: dataset for testing, columns name, target and identifier
            Arguments:
                columns (list of string): list of column names
                s3_url (string): s3 url without filename, default is used that you have passed at the init
            Returns:
                list of pandas.DataFrame [test, columns, target, identifier]
        """
        if s3_url is None:
            s3_url = self.s3_url
        datasets = []
        datasets_names = ['columns_names'] + columns
        # restore a dataset for each dataset_name in datasets_names
        for dataset_name in datasets_names:
            datasets.append(self.restore(f'{dataset_name}.csv', s3_url=s3_url))
        return datasets
    def convert_dtypes(self, dtypes, dataframe):
        """
        converts the dataframe column dtype with that specified
            Arguments:
                dtypes (dict): dictionary column: dtype
                train (pandas.DataFrame): dataframe with the columns of dtypes
            Returns:
                pandas.DataFrame converted
        """
        for column in dtypes.keys():
            if dtypes[column] in ['int64', 'float64', 'int', 'float']:
                dataframe[column] = pd.to_numeric(dataframe[column])
            elif dtypes[column] == 'datetime':
                dataframe[column] = pd.to_datetime(dataframe[column])
            elif dtypes[column] in ['bool', 'boolean']:
                bool_map = {'True': True, 'False': False}
                dataframe[column] = dataframe[column].map(bool_map)
            else:
                dataframe[column] = dataframe[column].astype(dtypes[column]) 
        return dataframe.convert_dtypes()
