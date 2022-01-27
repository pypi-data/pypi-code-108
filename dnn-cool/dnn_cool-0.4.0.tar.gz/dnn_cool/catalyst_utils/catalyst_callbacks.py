from catalyst.callbacks import BatchMetricCallback

from dnn_cool.losses.torch import BaseMetricDecorator


def catalyst_callbacks(criterion):
    callbacks = []
    for path, loss in criterion.get_leaf_losses().items():
        metric_decorator = BaseMetricDecorator(loss.task_name,
                                               loss.prefix,
                                               loss.metric,
                                               'loss',
                                               criterion.ctx)
        callbacks.append(BatchMetricCallback(f'loss_{path}', metric_decorator))
    for metric_name, metric_decorator in criterion.get_metrics():
        full_name = f'{metric_name}_{metric_decorator.prefix}{metric_decorator.task_name}'
        callback = BatchMetricCallback(full_name, metric_decorator)
        callbacks.append(callback)
    return callbacks
