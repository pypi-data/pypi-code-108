from functools import partial
from pathlib import Path
from typing import Optional

import joblib
import torch
from catalyst.contrib.callbacks import InferCallback
from catalyst.core import IRunner

from dnn_cool.serialization.base import to_dict_of_lists


class InferDictCallback(InferCallback):

    def __init__(self, infer_logdir: Optional[Path] = None,
                 out_key='logits',
                 loaders_to_skip=(),
                 task_flow=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loaders_to_skip = loaders_to_skip
        self.out_key = out_key
        self.predictions = {}
        self.targets = {}
        self.infer_logdir = infer_logdir
        self.task_flow = task_flow
        if self.infer_logdir is not None:
            self.infer_logdir.mkdir(exist_ok=True)
        self.__current_store = None

    def on_loader_start(self, state: IRunner):
        self.predictions[state.loader_key] = {}
        self.targets[state.loader_key] = {}

    def on_batch_end(self, state: IRunner):
        dct = state.output[self.out_key]
        if '_device|overall|_n' in dct:
            if self.__current_store is not None:
                self.__current_store(loader_name=state.loader_key)
            return
        dct = {key: value.detach().cpu().numpy() for key, value in dct.items() if key != 'gt'}
        loader_name = state.loader_key
        targets = state.input['targets']
        self.update_storage(loader_name, dct, targets)

    def on_dataparallel_gather(self, dct):
        self.__current_store = partial(self.update_storage, dct=dct, targets=dct['gt']['_targets'])

    def update_storage(self, loader_name, dct, targets):
        for key, value in dct.items():
            if key == 'gt':
                continue
            if key not in self.predictions[loader_name]:
                self.predictions[loader_name][key] = []
            if isinstance(value, list):
                self.predictions[loader_name][key].extend(value)
            else:
                self.predictions[loader_name][key].append(value)
        for key, value in targets.items():
            if key == 'gt':
                continue
            if key not in self.targets[loader_name]:
                self.targets[loader_name][key] = []
            if isinstance(value, list):
                self.targets[loader_name][key].extend(value)
            else:
                self.targets[loader_name][key].append(value.detach().cpu().numpy())

    def on_loader_end(self, state: IRunner):
        nested_dict = self.predictions[state.loader_key]
        self.predictions[state.loader_key] = to_dict_of_lists(nested_dict, nested_dict,
                                                              self.infer_logdir, 'logits', state.loader_key)
        self.targets[state.loader_key] = to_dict_of_lists(self.targets[state.loader_key], nested_dict,
                                                          self.infer_logdir, 'targets', state.loader_key)
        if self.task_flow is None:
            return
        for task_name, logits in self.predictions[state.loader_key].items():
            if task_name.startswith('indices|'):
                continue
            task_for_development = self.task_flow.get(task_name)
            loss = task_for_development.get_per_sample_criterion().loss
            targets = torch.tensor(self.targets[state.loader_key][task_name])
            logits = torch.tensor(logits)
            unreduced = loss(logits, targets).detach().cpu().numpy()
            out_dir = self.infer_logdir / state.loader_key / 'unrolled_loss'
            out_dir.mkdir(exist_ok=True)
            # Since the precondition has been applied already, we can make the assumption
            # that there are exactly 2 axes, one batch and one for the logits.
            reduced = unreduced.mean(axis=-1)
            joblib.dump(reduced, out_dir / f'{task_name}.pkl')