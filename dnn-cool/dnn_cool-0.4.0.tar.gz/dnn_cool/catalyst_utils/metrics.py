from functools import partial

import torch
from catalyst.metrics import accuracy, multilabel_accuracy

from dnn_cool.metrics.base import TorchMetric, NumpyMetric


class BinaryAccuracy(TorchMetric):

    def __init__(self):
        super().__init__(accuracy, decode=True)

    def _invoke_metric(self, outputs, targets, metric_args_dict):
        if len(outputs.shape) <= 1:
            outputs = outputs.unsqueeze(dim=-1)
        return self.metric_fn(outputs, targets, **metric_args_dict)[0]


class ClassificationAccuracy(TorchMetric):

    def __init__(self, metric_args=None):
        if metric_args is None:
            metric_args = {'topk': [1]}
        super().__init__(accuracy, decode=False, metric_args=metric_args)

    def _invoke_metric(self, outputs, targets, metric_args_dict):
        topk = metric_args_dict['topk']
        results = self.metric_fn(outputs, targets, **metric_args_dict)
        dict_metrics = dict(zip(topk, results))
        return dict_metrics

    def empty_precondition_result(self):
        res = {}
        for metric_arg in self.metric_args['topk']:
            res[metric_arg] = torch.tensor(0.)
        return res


class MultiLabelClassificationAccuracy(TorchMetric):

    def __init__(self, metric_args=None):
        if metric_args is None:
            metric_args = {'threshold': 0.5}
        super().__init__(multilabel_accuracy, decode=True, metric_args=metric_args)

    def _invoke_metric(self, outputs, targets, metric_args_dict):
        # the threshold does not actually matter, since the outputs are already decoded, i.e they are already 1 and 0
        return self.metric_fn(outputs, targets, **metric_args_dict)


def jaccard_threshold(y_true, y_pred, threshold):
    pred = y_pred > threshold
    true = y_true.astype(bool)
    return (true & pred).sum() / (true | pred).sum()


class JaccardIndex(NumpyMetric):

    def __init__(self, threshold=0.5):
        super().__init__(partial(jaccard_threshold, threshold=threshold))
