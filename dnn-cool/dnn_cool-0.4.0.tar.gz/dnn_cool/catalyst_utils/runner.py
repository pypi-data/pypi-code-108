from collections import OrderedDict
from functools import partial
from pathlib import Path
from shutil import copyfile
from typing import Dict, Tuple, Union
from typing import Mapping

import numpy as np
import torch
from catalyst.dl import SupervisedRunner, EarlyStoppingCallback
from catalyst.utils import load_checkpoint, unpack_checkpoint, any2device
from torch import nn
from torch import optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader, Dataset

from dnn_cool.catalyst_utils.infer_dict import InferDictCallback
from dnn_cool.catalyst_utils.catalyst_callbacks import catalyst_callbacks
from dnn_cool.serialization.loading import load_inference_results_from_directory
from dnn_cool.catalyst_utils.memory_balancing import ReplaceGatherCallback
from dnn_cool.catalyst_utils.interpretation import InterpretationCallback
from dnn_cool.tensorboard.base import TensorboardConverter, TensorboardConverters
from dnn_cool.split.serialization import save_split, runner_split
from dnn_cool.tasks.development.task_flow import TaskFlowForDevelopment
from dnn_cool.utils.torch import TransformedSubset


class DnnCoolSupervisedRunner(SupervisedRunner):

    def __init__(self, model: nn.Module,
                 full_flow: TaskFlowForDevelopment,
                 project_dir: Union[str, Path],
                 runner_name: str,
                 tensoboard_converters: TensorboardConverter = TensorboardConverter(),
                 early_stop: bool = True,
                 balance_dataparallel_memory: bool = False,
                 train_test_val_indices: Tuple[np.ndarray, np.ndarray, np.ndarray] = None):
        self.task_flow = full_flow

        self.default_criterion = self.task_flow.get_criterion()
        self.balance_dataparallel_memory = balance_dataparallel_memory

        self.default_callbacks = []
        if self.balance_dataparallel_memory:
            self.default_callbacks.append(ReplaceGatherCallback(self.task_flow))
        self.default_callbacks.extend(catalyst_callbacks(self.default_criterion))
        self.default_optimizer = partial(optim.AdamW, lr=1e-4)
        self.default_scheduler = ReduceLROnPlateau
        self.project_dir: Path = Path(project_dir)
        self.project_dir.mkdir(exist_ok=True)
        self.default_logdir = f'./logdir_{runner_name}'

        if early_stop:
            self.default_callbacks.append(EarlyStoppingCallback(patience=5))

        (self.project_dir / self.default_logdir).mkdir(exist_ok=True)
        if train_test_val_indices is None:
            n = len(self.task_flow.get_dataset())
            train_test_val_indices = runner_split(n, self.project_dir / self.default_logdir)
        else:
            save_split(self.project_dir / self.default_logdir, train_test_val_indices)
        self.train_test_val_indices = train_test_val_indices
        self.tensor_loggers = tensoboard_converters
        super().__init__(model=model)

    def train(self, *args, **kwargs):
        kwargs['criterion'] = kwargs.get('criterion', self.default_criterion)
        kwargs['model'] = kwargs.get('model', self.model)

        if 'optimizer' not in kwargs:
            model = kwargs['model']
            optimizable_params = filter(lambda p: p.requires_grad, model.parameters())
            kwargs['optimizer'] = self.default_optimizer(params=optimizable_params)

        if 'scheduler' not in kwargs:
            kwargs['scheduler'] = self.default_scheduler(kwargs['optimizer'])

        kwargs['logdir'] = kwargs.get('logdir', self.default_logdir)
        kwargs['logdir'] = self.project_dir / kwargs['logdir']
        kwargs['num_epochs'] = kwargs.get('num_epochs', 50)

        if 'loaders' not in kwargs:
            datasets, kwargs['loaders'] = self.get_default_loaders()

        default_callbacks = self.default_callbacks
        kwargs['callbacks'] = kwargs.get('callbacks', default_callbacks)
        super().train(*args, **kwargs)

    def infer(self, *args, **kwargs):
        default_datasets, default_loaders = self.get_default_loaders(shuffle_train=False)
        kwargs['loaders'] = kwargs.get('loaders', default_loaders)
        kwargs['datasets'] = kwargs.get('datasets', default_datasets)

        logdir = self.project_dir / Path(kwargs.get('logdir', self.default_logdir))
        kwargs['logdir'] = logdir
        store = kwargs.pop('store', True)
        infer_logdir = logdir / 'infer' if store else None
        interpretation_callback = self.create_interpretation_callback(infer_logdir=infer_logdir, **kwargs)
        infer_dict_callback = InferDictCallback(infer_logdir=infer_logdir, task_flow=self.task_flow)
        default_callbacks = OrderedDict([("interpretation", interpretation_callback),
                                         ("inference", infer_dict_callback)])
        if self.balance_dataparallel_memory:
            replace_gather_callback = ReplaceGatherCallback(self.task_flow, infer_dict_callback)
            default_callbacks["dataparallel_reducer"] = replace_gather_callback
        kwargs['callbacks'] = kwargs.get('callbacks', default_callbacks)
        kwargs['model'] = kwargs.get('model', self.model)
        kwargs.pop('loader_names_to_skip_in_interpretation', ())
        del kwargs['datasets']
        super().infer(*args, **kwargs)

    def create_interpretation_callback(self, infer_logdir, **kwargs) -> InterpretationCallback:
        tensorboard_converters = TensorboardConverters(
            logdir=kwargs['logdir'],
            tensorboard_loggers=self.tensor_loggers,
            datasets=kwargs.get('datasets', self.get_default_datasets(**kwargs))
        )
        loaders_to_skip = kwargs.get('loader_names_to_skip_in_interpretation', ())
        interpretation_callback = InterpretationCallback(self.task_flow.get_per_sample_criterion(),
                                                         infer_logdir=infer_logdir,
                                                         tensorboard_converters=tensorboard_converters,
                                                         loaders_to_skip=loaders_to_skip)
        return interpretation_callback

    def get_default_loaders(self, shuffle_train=True,
                            collator=None,
                            batch_size_per_gpu=32,
                            batch_sampler=None,
                            drop_last=False) -> Tuple[Dict[str, Dataset], Dict[str, DataLoader]]:
        datasets = self.get_default_datasets()
        train_dataset = datasets['train']
        val_dataset = datasets['valid']
        test_dataset = datasets['test']
        bs = max(batch_size_per_gpu, batch_size_per_gpu * torch.cuda.device_count())
        train_loader = DataLoader(train_dataset,
                                  batch_size=bs,
                                  shuffle=shuffle_train,
                                  collate_fn=collator,
                                  batch_sampler=batch_sampler,
                                  drop_last=drop_last)
        val_loader = DataLoader(val_dataset,
                                batch_size=bs,
                                shuffle=False,
                                collate_fn=collator)
        test_loader = DataLoader(test_dataset,
                                 batch_size=bs,
                                 shuffle=False,
                                 collate_fn=collator)
        loaders = OrderedDict({
            'train': train_loader,
            'valid': val_loader,
        })

        # Rename 'train' loader and dataset, since catalyst does not allow inference on train dataset.
        if not shuffle_train:
            loaders['infer'] = loaders['train']
            del loaders['train']
            datasets['infer'] = datasets['train']
            del datasets['train']
            loaders['test'] = test_loader
        return datasets, loaders

    def get_default_datasets(self, **kwargs) -> Dict[str, Dataset]:
        dataset = self.task_flow.get_dataset()
        if self.train_test_val_indices is None:
            raise ValueError(f'You must supply either a `loaders` parameter, or give `train_test_val_indices` via'
                             f'constructor.')
        train_indices, test_indices, val_indices = self.train_test_val_indices
        train_dataset = TransformedSubset(dataset, train_indices, sample_transforms=kwargs.get('train_transforms'))
        val_dataset = TransformedSubset(dataset, val_indices, sample_transforms=kwargs.get('val_transforms'))
        test_dataset = TransformedSubset(dataset, test_indices, sample_transforms=kwargs.get('val_transforms'))

        datasets = {
            'train': train_dataset,
            'valid': val_dataset,
            'test': test_dataset,
        }

        datasets['infer'] = datasets[kwargs.get('target_loader', 'valid')]
        return datasets

    def batch_to_model_device(self, batch) -> Mapping[str, torch.Tensor]:
        return any2device(batch, next(self.model.parameters()).device)

    def best(self) -> nn.Module:
        model = self.model
        checkpoint_path = str(self.project_dir / self.default_logdir / 'checkpoints' / 'best_full.pth')
        ckpt = load_checkpoint(checkpoint_path)
        unpack_checkpoint(ckpt, model)

        thresholds_path = self.project_dir / self.default_logdir / 'tuned_params.pkl'
        if not thresholds_path.exists():
            return model
        tuned_params = torch.load(thresholds_path)
        self.task_flow.task.get_decoder().load_tuned(tuned_params)
        return model

    def tune(self, loader_name='valid', store=True) -> Dict:
        res = self.load_inference_results()
        decoder = self.task_flow.task.get_decoder()
        tuned_params = decoder.tune(res['logits'][loader_name], res['targets'][loader_name])
        if store:
            out_path = self.project_dir / self.default_logdir / 'tuned_params.pkl'
            torch.save(tuned_params, out_path)
        return tuned_params

    def load_inference_results(self) -> Dict:
        logdir = self.project_dir / self.default_logdir
        return load_inference_results_from_directory(logdir)

    def load_tuned(self) -> Dict:
        tuned_params = torch.load(self.project_dir / self.default_logdir / 'tuned_params.pkl')
        self.task_flow.task.get_decoder().load_tuned(tuned_params)
        return tuned_params

    def evaluate(self, loader_name='test'):
        res = self.load_inference_results()
        self.load_tuned()
        evaluator = self.task_flow.get_evaluator()
        df = evaluator(res['logits'][loader_name], res['targets'][loader_name])
        df.to_csv(self.project_dir / self.default_logdir / 'evaluation.csv', index=False)
        return df

    def export_for_deployment(self, out_directory: Path):
        params_file = self.project_dir / self.default_logdir / 'tuned_params.pkl'
        if params_file.exists():
            copyfile(params_file, out_directory / 'tuned_params.pkl')
        torch.save(self.model.state_dict(), out_directory / 'state_dict.pth')


