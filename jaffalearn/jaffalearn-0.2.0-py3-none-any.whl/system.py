from collections import defaultdict

import torch
import torch.nn as nn


class AbstractSystem(nn.Module):
    def __init__(self):
        super().__init__()
        self.results = defaultdict(list)
        self.hyperparameters = {}

    @property
    def optimizer(self):
        raise NotImplementedError('`optimizer` unimplemented')

    @property
    def scheduler(self):
        pass

    def training_step(self, batch):
        raise NotImplementedError('`training_step` unimplemented')

    def training_epoch_end(self, **outputs):
        pass

    def validation_step(self, batch):
        raise NotImplementedError('`validation_step` unimplemented')

    def validation_epoch_end(self, **outputs):
        pass

    def test_step(self, batch):
        raise NotImplementedError('`test_step` unimplemented')

    def test_epoch_end(self, **outputs):
        pass

    def collate(self, **outputs):
        return tuple(map(torch.cat, outputs))

    def log(self, key, value):
        self.results[key].append(value)

    def summarize_results(self):
        return {k: sum(v) / len(v) for k, v in self.results.items()}

    def clear_results(self):
        self.results.clear()

    def add_hyperparameters(self, **kwargs):
        self.hyperparameters.update(kwargs)

    def serialize(self):
        return {
            'system_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'hyperparameters': self.hyperparameters,
        }

    def restore_state(self, checkpoint):
        # Ensure the system is on the correct device
        state_dict = checkpoint['system_state_dict']
        device = next(iter(state_dict.values())).device
        self.to(device)

        self.load_state_dict(state_dict)
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

    @classmethod
    def from_checkpoint(cls, checkpoint):
        params = checkpoint['hyperparameters']
        system = cls(**params)
        system.restore_state(checkpoint)
        return system


class SupervisedSystem(AbstractSystem):
    def __init__(self,
                 model,
                 criterion,
                 activation='softmax',
                 metrics=None,
                 np_metrics=None,
                 model_args=None,
                 ):
        super().__init__()

        self.model = model
        self.criterion = criterion
        self.metrics = metrics
        self.np_metrics = np_metrics

        if activation == 'softmax':
            self.activation = lambda x: x.softmax(dim=1)
        elif activation == 'sigmoid':
            self.activation = torch.sigmoid
        elif callable(activation):
            self.activation = activation
        elif activation is not None:
            raise ValueError(f"Invalid activation '{activation}'")

        self.add_hyperparameters(criterion=criterion,
                                 metrics=metrics,
                                 np_metrics=np_metrics,
                                 model_args=model_args,
                                 )

    def forward(self, x, logits=False):
        # Determine whether indexes were included in the input
        if isinstance(x, tuple):
            x, indexes = x
        else:
            indexes = None

        # Apply the model's forward pass
        y = self.model(x)
        if not logits and self.activation is not None:
            y = self.activation(y)

        if indexes is None:
            return y

        return {'y_pred': y, 'indexes': indexes}

    def training_step(self, batch):
        batch_x, batch_y = batch[:2]
        output = self(batch_x, logits=True)
        loss = self.criterion(output, batch_y)
        self.log('loss', loss.item())
        return loss

    def validation_step(self, batch):
        batch_x, batch_y = batch[:2]
        output = self(batch_x, logits=True)

        # Return everything that is needed for evaluation
        output = {'y_pred': output, 'y_true': batch_y}
        if len(batch) > 2:
            output['indexes'] = batch[2]
        return output

    def validation_epoch_end(self, y_pred, y_true, indexes=None):
        y_pred, y_true = self.collate(y_pred, y_true, indexes=indexes)
        self._evaluate('val', y_pred, y_true)

    def test_step(self, batch):
        return self.validation_step(batch)

    def test_epoch_end(self, y_pred, y_true, indexes=None):
        y_pred, y_true = self.collate(y_pred, y_true, indexes=indexes)
        self._evaluate('test', y_pred, y_true)

    def collate(self, y_pred, y_true=None, indexes=None):
        y_pred = torch.cat(y_pred)
        if y_true is not None:
            y_true = torch.cat(y_true)

        # Calculate clip-level predictions
        if indexes is not None:
            idx = torch.cat(indexes)[:, None].expand(-1, y_pred.shape[1])
            unique_idx, count = idx.unique(dim=0, return_counts=True)
            zeros = torch.zeros_like(unique_idx, dtype=torch.float)
            y_pred = zeros.scatter_add(0, idx, y_pred) / count[:, None]
            if y_true is not None:
                y_true = zeros.scatter_add(0, idx, y_true) / count[:, None]

        if y_true is None:
            return y_pred
        return y_pred, y_true

    def _evaluate(self, prefix, y_pred, y_true):
        # Compute loss for clip-level predictions
        loss = self.criterion(y_pred, y_true)
        self.log(f'{prefix}_loss', loss.item())

        if self.activation is not None:
            y_pred = self.activation(y_pred)

        # Evaluate performance using given metrics
        if self.metrics is not None:
            for name, fn in self.metrics.items():
                self.log(f'{prefix}_{name}', fn(y_pred, y_true).item())

        if self.np_metrics is not None:
            y_pred = y_pred.cpu().numpy()
            y_true = y_true.cpu().numpy()
            for name, fn in self.np_metrics.items():
                self.log(f'{prefix}_{name}', fn(y_pred, y_true))

    @classmethod
    def from_checkpoint(cls, checkpoint, model_fn):
        params = checkpoint['hyperparameters']
        model = model_fn(**params['model_args'])
        system = cls(model, **params)
        system.restore_state(checkpoint)
        return system
