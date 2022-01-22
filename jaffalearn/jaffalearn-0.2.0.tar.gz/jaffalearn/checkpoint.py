from pathlib import Path

import torch


class CheckpointHandler:
    def __init__(self, checkpoint_dir, serializable=None, path_format=None):
        self.serializable = serializable
        self.checkpoint_dir = Path(checkpoint_dir)

        if path_format is None:
            path_format = 'checkpoint.{epoch:02d}.pth'
        self.path_format = path_format

    def __call__(self):
        self.save()

    def save(self):
        checkpoint = self.serializable.serialize()
        torch.save(checkpoint, self.path(checkpoint['epoch']))

    def load(self, history=None, epoch=None, device=None):
        if history is not None:
            checkpoint_path = self.path_from_history(history)
        elif epoch is not None:
            checkpoint_path = self.path(epoch)
        else:
            raise ValueError('`epoch` and `history` are mutually exclusive')

        return torch.load(checkpoint_path, map_location=device)

    def path(self, epoch):
        return self.checkpoint_dir / self.path_format.format(epoch=epoch)

    def path_from_history(self, history, offset=0):
        if offset > len(history):
            raise RuntimeError('Checkpoint history exhausted')

        # Select the epoch specified by the offset (in descending order)
        epoch = history.index[-1 - offset]
        checkpoint_path = self.path(epoch)

        # Ensure the checkpoint file exists. If the file does not exist,
        # try a different epoch by increasing the offset.
        if not Path(checkpoint_path).exists():
            print(f'Warning: {checkpoint_path} not found')
            return self.path_from_history(history, offset + 1)

        return checkpoint_path
