from .base_logger import Logger

from torch.utils.tensorboard import SummaryWriter

class TensorboardLogger(Logger):
    def __init__(self, base_root, runname=None, time_suffix=True, mode='train') -> None:
        super().__init__(base_root, runname, time_suffix, mode)

        self.writer = SummaryWriter(self.res_dir)
        

    def log_metric(self, name, value, global_step):
        self.writer.add_scalar(name, value, global_step=global_step)

