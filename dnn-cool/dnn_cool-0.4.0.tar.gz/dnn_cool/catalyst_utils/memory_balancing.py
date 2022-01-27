from functools import partial

import torch
from catalyst.callbacks import BatchMetricCallback
from catalyst.core import Callback, CallbackOrder, IRunner
from torch import nn
from torch.nn import DataParallel

from dnn_cool.catalyst_utils.base import should_skip_loader
from dnn_cool.catalyst_utils.interpretation import InterpretationCallback
from dnn_cool.utils.base import any_value


class DeviceReducingDataParallel(DataParallel):

    def __init__(self, module: nn.Module, task_flow, infer_dict_callback):
        super().__init__(module)
        tasks_dict = task_flow.get_all_children()
        self.full_paths = []
        for full_path, task_for_development in tasks_dict.items():
            if task_for_development.task.is_train_only():
                continue
            self.full_paths.append(full_path)
        criterion = task_flow.get_criterion()
        per_sample_criterion = task_flow.get_per_sample_criterion(ctx=criterion.get_device_reduced_ctx())
        leaf_losses = criterion.get_leaf_losses()
        metrics = criterion.get_metrics()
        self._reducing_func = partial(reduce_on_device,
                                      criterion=criterion,
                                      per_sample_criterion=per_sample_criterion,
                                      leaf_criterions=leaf_losses,
                                      metrics=metrics)
        self.infer_dict_callback = infer_dict_callback
        self.ctx = criterion.ctx
        self.r_device_metrics = False
        self.r_leaf_losses = False
        self.r_per_sample_losses = False
        self.store_inference_results = self.infer_dict_callback is not None

    def gather(self, outputs, output_device):
        self.ctx.clear()
        device_reduced_results = []
        dct = {
            'gt': {'_targets': {}}
        }
        for full_path in self.full_paths:
            dct[full_path] = []
            dct[f'precondition|{full_path}'] = []

        ctx_reductions = {}
        for i in range(len(outputs)):
            reduced_with_grad, reduced = self._reducing_func(outputs=outputs[i],
                                                             targets=outputs[i]['gt']['_targets'],
                                                             r_device_metrics=self.r_device_metrics,
                                                             r_leaf_losses=self.r_leaf_losses,
                                                             r_per_sample_losses=self.r_per_sample_losses)
            device_reduced_results.append(reduced_with_grad)
            for key, value in reduced.items():
                if key not in ctx_reductions:
                    ctx_reductions[key] = []
                value = value.detach().cpu()
                if len(value.shape) == 0:
                    value = value.unsqueeze(0)
                ctx_reductions[key].append(value)

            if self.store_inference_results:
                for full_path in self.full_paths:
                    dct[full_path].append(outputs[i][full_path].detach().cpu().numpy())
                    precondition_path = f'precondition|{full_path}'
                    dct[precondition_path].append(outputs[i][precondition_path].detach().cpu().numpy())
                    np_targets = outputs[i]['gt']['_targets'][full_path].detach().cpu().numpy()
                    if full_path not in dct['gt']['_targets']:
                        dct['gt']['_targets'][full_path] = []
                    dct['gt']['_targets'][full_path].append(np_targets)

        if self.infer_dict_callback is not None:
            self.infer_dict_callback.on_dataparallel_gather(dct)
        gathered = super().gather(device_reduced_results, output_device)
        additional_metrics = {key: torch.cat(value, dim=0) for key, value in ctx_reductions.items()}

        for key, value in additional_metrics.items():
            self.ctx[key] = value
        return gathered

    def reset_device_reducing_tasks(self):
        self.r_device_metrics = False
        self.r_leaf_losses = False
        self.r_per_sample_losses = False
        self.store_inference_results = len(self.callbacks) > 0


class ReplaceGatherCallback(Callback):

    def __init__(self, task_flow, infer_dict_callback=None):
        super().__init__(CallbackOrder.External)
        self.task_flow = task_flow
        self.infer_dict_callback = infer_dict_callback

    def on_stage_start(self, runner: "IRunner"):
        if isinstance(runner.model, DataParallel):
            runner.model = DeviceReducingDataParallel(runner.model.module, self.task_flow, self.infer_dict_callback)

    def on_loader_start(self, runner: "IRunner"):
        model = runner.model
        if not isinstance(model, DeviceReducingDataParallel):
            return
        for idx, callback in runner.callbacks.items():
            if isinstance(callback, InterpretationCallback):
                model.r_per_sample_losses = not should_skip_loader(runner, callback.loaders_to_skip)
            if isinstance(callback, BatchMetricCallback):
                model.r_device_metrics = True
                model.r_leaf_losses = True


def reduce_on_device(criterion,
                     per_sample_criterion,
                     leaf_criterions,
                     metrics,
                     outputs,
                     targets,
                     r_device_metrics,
                     r_leaf_losses,
                     r_per_sample_losses):
    loss = criterion(outputs, targets)
    any_tensor = any_value(targets)
    n = len(any_tensor)
    criterion_n = torch.tensor(n, dtype=any_tensor.dtype, device=any_tensor.device)
    reduced_with_grad = {
        f'_device|{criterion.prefix}{criterion.task_name}|loss': loss,
        f'_device|{criterion.prefix}{criterion.task_name}|_n': criterion_n,
        f'_device|overall|loss': loss,
        f'_device|overall|_n': criterion_n
    }
    reduced = {}

    with torch.no_grad():
        if r_device_metrics:
            compute_device_metrics(reduced, any_tensor, metrics, outputs, targets)
        if r_leaf_losses:
            compute_leaf_losses(leaf_criterions, outputs, reduced, targets)
        if r_per_sample_losses:
            compute_per_sample_losses(reduced, per_sample_criterion, outputs, targets, n)

    return reduced_with_grad, reduced


def compute_leaf_losses(leaf_criterions, outputs, reduced, targets):
    for path, leaf_loss in leaf_criterions.items():
        reduced[f'_device|{path}|loss'] = leaf_loss(outputs, targets).loss_items
        reduced[f'_device|{path}|_n'] = outputs[f'precondition|{path}'].sum()


def compute_per_sample_losses(reduced, per_sample_criterion, outputs, targets, n):
    per_sample_losses = per_sample_criterion(outputs, targets)
    for key, value in per_sample_losses.items():
        if key.startswith('indices'):
            value += (n * value.device.index)
        if len(value.shape) == 0:
            value = value.unsqueeze(0)
        reduced[f'_device|{key}|loss_per_sample'] = value
        if not key.startswith('indices') and key != 'overall':
            reduced[f'_device|{key}|_n'] = outputs[f'precondition|{key}'].sum()


def compute_device_metrics(reduced, any_tensor, metrics, outputs, targets):
    for metric_name, metric in metrics:
        path = f'{metric.prefix}{metric.task_name}'
        full_name = f'{path}|{metric_name}'
        metric_res = metric(outputs, targets)
        if isinstance(metric_res, dict):
            for key, value in metric_res.items():
                value = torch.as_tensor(value, dtype=any_tensor.dtype, device=any_tensor.device)
                if len(value.shape) == 0:
                    value = value.unsqueeze(0)
                reduced[f'_device|{full_name}_{key}'] = value
        else:
            value = torch.as_tensor(metric_res, dtype=any_tensor.dtype, device=any_tensor.device)
            if len(value.shape) == 0:
                value = value.unsqueeze(0)
            reduced[f'_device|{full_name}'] = value
        reduced[f'_device|{path}|_n'] = outputs[f'precondition|{metric.prefix}{metric.task_name}'].sum()