from functools import partial

import torch

from sklearn.metrics import f1_score, precision_score, recall_score
from torch import nn


class TorchMetric:

    def __init__(self, metric_fn, decode=True, metric_args=None):
        if metric_args is None:
            metric_args = {}
        self.activation = None
        self.decoder = None
        self.metric_fn = metric_fn
        self.metric_args = metric_args
        self._decode = decode
        self._is_binded = False

    def bind_to_task(self, task):
        self._is_binded = True
        self.activation = task.get_activation()
        self.decoder = task.get_decoder()

    def __call__(self, outputs, targets, activate=True):
        if not self._is_binded:
            raise ValueError(f'The metric is not binded to a task, but is already used.')
        outputs = torch.as_tensor(outputs)
        targets = torch.as_tensor(targets)

        if activate:
            outputs = self.activation(outputs)
        if self._decode:
            outputs = self.decoder(outputs)
        return self._invoke_metric(outputs, targets, self.metric_args)

    def _invoke_metric(self, outputs, targets, metric_args_dict):
        return self.metric_fn(outputs, targets, **metric_args_dict)


class NumpyMetric(TorchMetric):

    def __init__(self, metric_fn, decode=True):
        super().__init__(metric_fn, decode)

    def _invoke_metric(self, outputs, targets, metric_args_dict):
        if isinstance(outputs, torch.Tensor):
            outputs = outputs.detach().cpu().numpy()
        if isinstance(targets, torch.Tensor):
            targets = targets.cpu().numpy()
        return self.metric_fn(outputs, targets, **metric_args_dict)


class BinaryF1Score(NumpyMetric):

    def __init__(self):
        super().__init__(f1_score)


class BinaryPrecision(NumpyMetric):

    def __init__(self):
        super().__init__(precision_score)


class BinaryRecall(NumpyMetric):

    def __init__(self):
        super().__init__(recall_score)


class ClassificationNumpyMetric(NumpyMetric):

    def __init__(self, metric_fn, decode=True):
        super().__init__(metric_fn, decode=decode)

    def _invoke_metric(self, outputs, targets, metric_args_dict):
        if isinstance(outputs, torch.Tensor):
            outputs = outputs.detach().cpu().numpy()
        if isinstance(targets, torch.Tensor):
            targets = targets.cpu().numpy()
        outputs = outputs[..., 0]
        return self.metric_fn(outputs, targets, **metric_args_dict)


class ClassificationF1Score(ClassificationNumpyMetric):

    def __init__(self):
        super().__init__(partial(f1_score, average='micro'))


class ClassificationPrecision(ClassificationNumpyMetric):

    def __init__(self):
        super().__init__(partial(precision_score, average='micro'))


class ClassificationRecall(ClassificationNumpyMetric):

    def __init__(self):
        super().__init__(partial(recall_score, average='micro'))


class MeanAbsoluteError(TorchMetric):

    def __init__(self, decode=False):
        super().__init__(nn.L1Loss(), decode)



