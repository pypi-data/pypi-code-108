import os
import datetime
from pathlib import Path

import pandas as pd
import luigi

PROCESSED_DIR = 'processed'
ROLLUP_DIR = 'rollups'

class PrepareDataTask(luigi.Task):
    def __init__(self):
        super().__init__()
        self.last_processed_id = 0
        if os.path.exists('last_processed_id.txt'):
            try:
                with open('last_processed_id.txt', 'r') as f:
                    self.last_processed_id = int(f.read())
            except Exception as e:
                print('Error reading last_processed_id.txt')

        self.last_id = self.last_processed_id
        self.df = pd.read_json('test_data/trip_data.json')
        # Simulate only getting the latest (unprocessed).
        self.df = self.df[self.df['id'] > self.last_processed_id]
        if len(self.df):
            self.last_id = int(self.df.iloc[-1]['id'])

    def requires(self):
        return None

    def run(self):
        if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)

        # Simulate work
        #import time
        #time.sleep(10)

        # Simulate error
        #import random
        #if random.random() > 0.5:
        #    raise Exception('Fake error')

        output_path = f'{PROCESSED_DIR}/processed_{self.last_id}.parquet'
        self.df.to_parquet(output_path)

        with open('last_processed_id.txt', 'w') as f:
            f.write(f'{self.last_id}')

    def output(self):
        output_path = f'{PROCESSED_DIR}/processed_{self.last_id}.parquet'
        return luigi.LocalTarget(output_path)


class RollupTask(luigi.Task):
    date_param = luigi.DateParameter(default=datetime.date.today())
    rollup_dir = Path(ROLLUP_DIR)

    def _output_path(self):
        return f'{ROLLUP_DIR}/rollup_{self.date_param}.parquet'

    def requires(self):
        return PrepareDataTask()

    def run(self):
        if not os.path.exists(ROLLUP_DIR):
            os.makedirs(ROLLUP_DIR)

        data_dir = Path(PROCESSED_DIR)
        df = pd.concat(
            pd.read_parquet(parquet_file)
            for parquet_file in data_dir.glob('*.parquet')
        )

        # Average travel times
        rollup = df.groupby(['origin_id', 'destination_id'])['travel_time'].mean().to_frame()
        rollup.to_parquet(self._output_path())

    def output(self):
        return luigi.LocalTarget(self._output_path())

if __name__ == '__main__':
    luigi.run()
