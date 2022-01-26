import os
import random

from .logger import Logger
from .utils import CSVIO as csv

bird = Logger()


class Excel:
    def __init__(self, excel_file: str):
        import pandas as pd
        self.xls = pd.ExcelFile(excel_file)
        bird.info(f'Load {excel_file} SUCCESS')

    def to_csv(self, target_dir: str = '/tmp/'):
        import pandas as pd
        for sheet in self.xls.sheet_names:
            _df = pd.read_excel(self.xls, sheet_name=sheet)
            _f = os.path.join(target_dir, sheet + '.csv')
            bird.info(f'Export [{sheet}] to {_f}')
            _df.to_csv(_f, index=False)


def excel2csv(file_name: str, target_dir: str = '/tmp/'):
    Excel(file_name).to_csv(target_dir)


class CSV:
    def __init__(self, file_name: str) -> None:
        self.data = csv.read(file_name)
        self._inspect(self.data)

    def _inspect(self, csv_list: list) -> None:
        ''' Get CSV information of file
        '''
        self.length = len(csv_list)
        self.width = len(csv_list[0])

    def __repr__(self) -> str:
        _str = '\n'.join(f'{k:<15}: {self.__dict__[k]}'
                         for k in ('length', 'width'))
        _str += '\n{:<15}: {}'.format('First line', self.data[0])
        _str += '\n{:<15}: {}'.format('Sample', random.sample(self.data, 1)[0])
        return _str
