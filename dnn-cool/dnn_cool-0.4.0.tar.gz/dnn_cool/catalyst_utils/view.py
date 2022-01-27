from functools import cached_property
from pathlib import Path
from typing import Union, Optional, Dict

import torch
from torch import nn

from dnn_cool.serialization.loading import load_inference_results_from_directory
from dnn_cool.split.serialization import read_split
from dnn_cool.tasks.task_flow import TaskFlow
from dnn_cool.utils.torch import load_model_from_export


class DnnCoolRunnerView:

    def __init__(self, full_flow: TaskFlow, model: nn.Module,
                 project_dir: Union[str, Path], runner_name: str):
        self.project_dir = Path(project_dir)
        self.full_flow = full_flow
        self.model = model
        self.runner_name = runner_name
        self.default_logdir_name = f'./logdir_{runner_name}'

    def best(self) -> nn.Module:
        return self.load_model_from_checkpoint('best')

    def last(self) -> nn.Module:
        return self.load_model_from_checkpoint('last')

    def from_epoch(self, i) -> nn.Module:
        return self.load_model_from_checkpoint(f'train.{i}')

    def load_model_from_export(self, out_directory: Union[str, Path]) -> nn.Module:
        return load_model_from_export(self.model, self.full_flow, out_directory)

    def load_model_from_checkpoint(self, checkpoint_name) -> nn.Module:
        model = self.model
        logdir = self.project_dir / self.default_logdir_name
        checkpoint_path = str(logdir / 'checkpoints' / f'{checkpoint_name}.pth')
        model.load_state_dict(torch.load(checkpoint_path)['model_state_dict'])
        thresholds_path = logdir / 'tuned_params.pkl'
        if not thresholds_path.exists():
            return model
        tuned_params = torch.load(thresholds_path)
        self.full_flow.get_decoder().load_tuned(tuned_params)
        return model

    def load_tuned_params(self) -> Optional[Dict]:
        logdir = self.project_dir / self.default_logdir_name
        thresholds_path = logdir / 'tuned_params.pkl'
        if not thresholds_path.exists():
            return None
        return torch.load(thresholds_path)

    def load_inference_results(self) -> Dict:
        logdir = self.project_dir / self.default_logdir_name
        return load_inference_results_from_directory(logdir)

    def load_train_test_val_split(self):
        return read_split(self.project_dir / self.default_logdir_name)

    @cached_property
    def train_test_val_indices(self):
        return self.load_train_test_val_split()

    @cached_property
    def inference_results(self):
        return self.load_inference_results()

    @cached_property
    def evaluation_df(self):
        import pandas as pd
        return pd.read_csv(self.project_dir / self.default_logdir_name / 'evaluation.csv')

    def summarize_loss_values(self, loader_name, task_name):
        interpretations = self.inference_results['interpretations'][loader_name]
        loss_values = interpretations[task_name]
        loss_local_indices = interpretations[f'indices|{task_name}']
        loader_idx = ['infer', 'test', 'valid'].index(loader_name)
        global_loader_indices = self.train_test_val_indices[loader_idx]
        mask = loss_local_indices >= 0
        task = self.full_flow.get_all_children()[task_name]
        return {
            'global_idx': global_loader_indices[loss_local_indices[mask]],
            'loss_values': loss_values[mask],
            'task': task.get_name()
        }

    def worst_examples(self, loader_name, task_name, n):
        return self.extremal_examples(loader_name, task_name, n, -1)

    def best_examples(self, loader_name, task_name, n):
        return self.extremal_examples(loader_name, task_name, n, 1)

    def extremal_examples(self, loader_name, task_name, n, mult):
        res = self.summarize_loss_values(loader_name, task_name)
        sorter = (mult * res['loss_values']).argsort()
        res['global_idx_sorted'] = res['global_idx'][sorter]
        top_n_idx = res['global_idx'][sorter[:n]]
        res[f'global_idx_{n}'] = top_n_idx
        return res
