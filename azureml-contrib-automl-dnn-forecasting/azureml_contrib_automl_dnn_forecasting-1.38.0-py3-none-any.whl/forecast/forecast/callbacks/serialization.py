"""Creates a checkpoint containing the model state, epoch, and optionally optimizer/other state."""

import os.path as osp
from typing import Optional

import torch
from torch.optim import Optimizer

from forecast.callbacks import Callback


class CheckpointCallback(Callback):
    """Creates a checkpoint containing the model state, epoch, and optionally optimizer/other state."""

    def __init__(self, checkpoint_epochs: int, out_dir: str, optim: Optional[Optimizer] = None, **kwargs):
        """Creates a checkpoint containing the model state, epoch, and optionally optimizer state.

        Parameters
        ----------
        checkpoint_epochs: int
            A checkpoint will be created every `checkpoint_epochs` epochs
        out_dir: str
            Checkpoints will be created in this directory
        optim: Optimizer, optional
            If specified, the optimizer's state will be persisted in the checkpoint
        kwargs: dict
            A dict of (key, value) paies which will be persisted in the checkpoint with a name of `key` and value of
            `value.state_dict()`.

        """
        super().__init__()
        self._checkpoint_epochs = checkpoint_epochs
        self._epochs = 0
        self._out_dir = out_dir
        self._optim = optim
        self._other_args = kwargs

    def on_train_val_epoch_end(self, epoch: int) -> None:
        """Creates the checkpoint every N epochs.

        Parameters
        ----------
        epoch: int
            The current epoch

        Returns
        -------
        None

        """
        self._epochs = epoch
        if (self._epochs + 1) % self._checkpoint_epochs == 0:
            save_dict = {
                'model': self._model.state_dict(),
                'epoch': epoch
            }

            if self._optim:
                save_dict['optimizer'] = self._optim.state_dict()

            if self._other_args:
                for k, v in self._other_args.items():
                    save_dict[k] = v

            torch.save(save_dict, osp.join(self._out_dir, f'epoch_{epoch}.pt'))
