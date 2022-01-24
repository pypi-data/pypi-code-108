import pytest
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import ExponentialLR

from forecast.callbacks import CallbackList, LRScheduleCallback, MetricCallback

@pytest.fixture(scope='function')
def metric_callback():
    train_metrics = {}
    val_metrics = {}
    return MetricCallback(train_metrics, val_metrics)


def invoke_callback_steps(cb):
    cb.on_train_begin()
    cb.on_train_epoch_begin(0)
    cb.on_train_batch_begin(0, 0)
    cb.on_train_batch_before_backward(torch.tensor(0))
    cb.on_train_batch_before_step()
    cb.on_train_batch_end(0, 0, 0)
    cb.on_train_epoch_end(0, 0, {})

    cb.on_val_begin(0)
    cb.on_val_batch_begin(0, 0)
    cb.on_val_batch_end(0, 0, 0)
    cb.on_val_end(0, 0, {})
    cb.on_train_val_epoch_end(0)
    cb.on_train_end()

    cb.on_predict_begin()
    cb.on_predict_batch_begin(0)
    cb.on_predict_batch_end(0)
    cb.on_predict_end()


def test_empty_metric_callback(metric_callback):
    invoke_callback_steps(metric_callback)


# def test_callback_list(metric_callback):
#     conv = nn.Conv1d(3, 1, 1)
#     optim = SGD(conv.parameters(), 0.001)
#     sched = ExponentialLR(optim, 0.99)
#     lr = LRScheduleCallback(sched)
#
#     cb_list = CallbackList([metric_callback, lr], model=)




