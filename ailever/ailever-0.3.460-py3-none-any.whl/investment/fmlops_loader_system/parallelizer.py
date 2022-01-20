from ailever.investment import __fmlops_bs__ as fmlops_bs
from .integrated_loader import Loader
from .._base_transfer import DataTransferCore

from datetime import datetime
import os
import re
from tqdm import tqdm
import numpy as np
import pandas as pd

dataset_dirname = fmlops_bs.core['FS'].path
class ParallelizationLoader:
    def __init__(self):
        self.loader = Loader()

    def prllz_loader(self, baskets=None, path=dataset_dirname, object_format='csv', base_column='close', date_column='date', period=100):
        self.loader.ohlcv_loader(baskets=baskets)
        self.prllz = Parallelizer(baskets=baskets,
                             path=path,
                             object_format=object_format,
                             base_column=base_column,
                             date_column=date_column,
                             truncate=period)
        self.datacore = DataTransferCore()
        self.datacore.ndarray = self.prllz.ndarray
        self.datacore.pdframe = self.prllz.pdframe
        return self.datacore

    @staticmethod
    def parallelize(baskets=None, path=dataset_dirname, object_format='csv', base_column='close', date_column='date', columns=None):
        assert bool(columns), 'The columns argument must be defined'
        if isinstance(columns, pd.core.indexes.base.Index):
            columns = columns.to_list()

        if bool(baskets):
            baskets = list(map(lambda x: x + '.' + object_format, baskets))
            serialized_objects = filter(lambda x: x in baskets, filter(lambda x: x[-len(object_format):] == object_format, os.listdir(path)))
        else:
            serialized_objects = filter(lambda x: x[-len(object_format):] == object_format, os.listdir(path))
        
        base_frame = None
        for so in tqdm(serialized_objects):
            df = pd.read_csv(os.path.join(path, so))
            if df.columns.to_list() == columns:
                df[date_column] = pd.to_datetime(df[date_column])
                df = df.set_index(date_column)[base_column].to_frame().reset_index()
                df.columns = [date_column, so[:-len(object_format)-1]]
            else:
                continue

            if base_frame is not None:
                base_frame = pd.merge(base_frame, df, on=date_column, how='outer')
            else:
                base_frame = df

        base_frame = base_frame.sort_values(by=date_column).reset_index().drop('index', axis=1).set_index(date_column)
        base_frame.to_csv('.prllz_cache'+'.'+object_format)

        datacore = DataTransferCore()
        datacore.pdframe = base_frame
        datacore.ndarray = base_frame.values
        return datacore


class Parallelizer:
    def __init__(self, baskets, object_format, base_column, date_column, truncate, path=dataset_dirname):
        self.baskets = baskets
        self.origin_path = os.getcwd()
        self.serialization_path = path
        self.base_column = base_column
        self.date_column = date_column
        self.truncated_period = truncate
        self.ndarray = getattr(self, '_'+object_format)(to='ndarray')
        self.pdframe = getattr(self, '_'+object_format)(to='pdframe')
 
    def _csv(self, to):
        if not self.baskets:
            serialized_objects = [file for file in os.listdir(self.serialization_path) if os.path.isfile(os.path.join(self.serialization_path, file))]
        else:
            serialized_objects = list(map(lambda x: x+'.csv', self.baskets))
        serialized_objects = list(filter(lambda x: (x[-3:] == 'csv') and ('_' not in x) and ('+' not in x), serialized_objects))
        ticker_names = list(map(lambda x: x[:-re.search('[.]', x[::-1]).span()[1]], serialized_objects))
        
        so_path = os.path.join(self.serialization_path, serialized_objects.pop(0))
        base_init_frame = pd.read_csv(so_path)
        base_period = base_init_frame[self.date_column].values[-self.truncated_period:]
        self.base_period = base_period
        base_array = base_init_frame[self.base_column].values[-self.truncated_period:]
        mismatching = list()
        for so in serialized_objects:
            so_path = os.path.join(self.serialization_path, so)
            appending_frame = pd.read_csv(so_path)
            try:
                appending_period = appending_frame[self.date_column].values[-self.truncated_period:]
            except:
                print(f'FAIL TO LOAD : {so}')
                continue
            checker = base_period == appending_period
            if not checker.all():
                so = so[:-re.search('[.]', so[::-1]).span()[1]]
                mismatching.append(so)
                continue
            appending_array = appending_frame[self.base_column].values[-self.truncated_period:]
            base_array = np.c_[base_array, appending_array]
        
        for m_ticker in mismatching:
            del ticker_names[ticker_names.index(m_ticker)]

        if to == 'ndarray':
            print('[PARALLELIZER] MISMATCHED TiCKERS FOR GIVEN PERIOD :', mismatching)
            return base_array

        elif to == 'pdframe':
            base_frame = pd.DataFrame(data=base_array, columns=ticker_names)
            base_frame.insert(0, self.date_column, pd.to_datetime(base_period))
            return base_frame.set_index(self.date_column)

    
