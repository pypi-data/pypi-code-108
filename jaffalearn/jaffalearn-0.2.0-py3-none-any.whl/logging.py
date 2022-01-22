from pathlib import Path

import pandas as pd

from torch.utils.tensorboard import SummaryWriter


class Logger:
    def __init__(self, system, log_dir, overwrite=False):
        self.log_path = Path(log_dir) / 'history.csv'

        self.system = system
        self.tb_writer = None

        # Remove any previous TensorBoard log files
        if overwrite:
            for path in self.log_path.parent.glob('*tfevents*'):
                print(f'Deleting {path}')
                path.unlink()

        # Read from existing log file if applicable
        if overwrite or not self.log_path.exists():
            self.history = pd.DataFrame()
            self.history.index.name = 'epoch'
        else:
            self.history = pd.read_csv(self.log_path, index_col=0)

    def __call__(self):
        self.step()

    def step(self):
        # Print results to stdout
        results = self.system.summarize_results()
        print(', '.join(['{}: {:.4f}'.format(k, v)
                         for k, v in results.items()]))

        # Write results to TensorBoard log file
        epoch = len(self.history)
        if self.tb_writer is None:
            self.tb_writer = SummaryWriter(self.log_path.parent)
        for key, value in results.items():
            self.tb_writer.add_scalar(key, value, epoch)
        self.tb_writer.file_writer.flush()

        # Write results to CSV file
        self.history = self.history.append(results, ignore_index=True)
        self.history.to_csv(self.log_path)

        self.system.clear_results()

    def truncate(self, epoch):
        self.history = self.history.iloc[:epoch]
        self.history.to_csv(self.log_path)

    def close(self):
        if self.tb_writer is not None:
            self.tb_writer.close()
