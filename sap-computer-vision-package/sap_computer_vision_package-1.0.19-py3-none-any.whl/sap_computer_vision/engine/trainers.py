"""This module contain Trainer and Hook for default training routines.
"""
import logging
import operator
import math
import pathlib
from typing import Callable, List, Union
from detectron2.data.build import build_detection_train_loader

import numpy as np

from detectron2.engine import DefaultTrainer, HookBase
from detectron2.engine.hooks import EvalHook, BestCheckpointer
from detectron2.utils import comm, logger
from detectron2.utils.logger import log_first_n
from detectron2.config import CfgNode
from detectron2.evaluation import (
    verify_results,
)

import detectron2.data.transforms as T_
import torch

from fvcore.common.checkpoint import Checkpointer
from numpy import logical_not

from sap_computer_vision.data.samplers import PKTripletSampler, TripletReservoirSampler, PredictReservoirHook, PKTripletStrategySwitcher
from sap_computer_vision.data.data_build import build_detection_test_loader_batched, DatasetMapperWithAdditionalAugmentaions
from sap_computer_vision.evaluators import ContrastiveEvaluator, ImageClassificationEvaluator, ObjectDetectionEvaluator
from sap_computer_vision.data import build_classification_train_loader, build_classification_test_loader_batched, DatasetMapperClassification


logger = logging.getLogger(__name__)


class LoadBest(HookBase):
    """This hook loads the best. Only usable in combination with BestCheckpointer hook."""

    def __init__(self, best_checkpoint_hook: BestCheckpointer):
        """Create hook to load the best model at the end of the training.

        Parameters
        ----------
        best_checkpoint_hook: BestCheckpointer
            Instance of the BestCheckpointer hook.
        """
        self.checkpointer = best_checkpoint_hook._checkpointer
        self.model_prefix = best_checkpoint_hook._file_prefix

    def after_train(self):
        if self.trainer.iter + 1 >= self.trainer.max_iter:
            path = pathlib.Path(self.checkpointer.save_dir) / f'{self.model_prefix}.pth'
            if path.is_file():
                logger.info(f'Loading best model from checkpoint {path}')
                self.checkpointer.load(str(path))
            else:
                logger.warning('Not loading any model, because no best model was found!')


class EarlyStoppingHook(EvalHook):
    """Hook to perform early stopping. It uses the same eval condition as the EvalHook.
    """
    def __init__(self,
                 eval_period: int,
                 patience: int,
                 delta: float,
                 get_last_eval_result_f: Callable,
                 metric_name: Union[None, str]=None,
                 mode: str='max'):
        """

        Parameters
        ----------
        eval_period: int
            This class is a subclass of the EvalHook and shares uses its way of
            trigering an evaluation to check for an early stop. The evaluation is
            simply triggered every 'eval_period' steps.
        patience: int
            Number of evaluation without an improvement without stopping the
            training.
        delta: float
            Minimal Improvement.
        get_last_eval_result_f: callable
            Function returning a dict with the last evaluation results or
            the value of the a specific metric directly.
            When combined with EvalHook it is probably advisable
            to retrieve its results and not to redo the evaluation.
            Check EarlyStoppingTrainer.build_hooks as an example.
        metric_name: None or str, optional, default=None
            Name of the metric used to decide on an early stop.
            In cases 'get_last_eval_result_f' returns a value
            directly the metric_name is ignored. If the function
            returns a dict the metric_name is the key of the metric.
        mode: str, optional, default='max'
            'max' if the metric should be maximized.
            'min' if the metric should be minimized.
        """
        super().__init__(eval_period, None)
        self.patience = patience
        self.delta = delta
        self.metric_name = metric_name
        self.best_result = None
        self.unimproved_evals = 0
        if mode == 'max':
            self.is_better = lambda x: (self.best_result + self.delta) <= x
        elif mode == 'min':
            self.is_better = lambda x: (self.best_result - self.delta) >= x
        else:
            ValueError(f'`mode` (cfg.SOLVER.EARLY_STOPPING.MODE) for EarlyStopping has to either `max` or `min`. Got {mode}!')
        self.get_last_result = get_last_eval_result_f

    def _do_eval(self):
        new_result = self.get_last_result()
        if isinstance(new_result, dict):
            if self.metric_name is None:
                new_result = None
                log_first_n(
                    logging.WARN,
                    "The provided result function returns a dict. Please specifiy"
                    " the name of the metric for early stopping!",
                    name=__name__)
            else:
                try:
                    new_result = new_result[self.metric_name]
                except KeyError:
                    log_first_n(
                        logging.WARN,
                        f"Not metric {self.metric_name} found in the result.",
                        name=__name__)
                    new_result = None
        if new_result is None:
            return  # No evaluation result found!
        if self.best_result is None:
            self.best_result = new_result
        else:
            if self.is_better(new_result):
                was_stalling = self.unimproved_evals > 0
                self.unimproved_evals = 0
                self.best_result = new_result
                if was_stalling:
                    logger.info('The model performance improved again. Early stopping countered was resetted')
            else:
                self.unimproved_evals += 1
                logger.info(f'The performance has not improved in the last'
                            f' {self.unimproved_evals} evaluation (patience: {self.patience}).')

        if self.unimproved_evals >= self.patience:
            msg = 'No improvements of the model performance'
            msg += (f" ({self.metric_name}) " if self.metric_name is None else ' ')
            msg += f'in the last {self.patience} evaluations.'
            logger.info(msg)
            raise EarlyStop


    def after_train(self):
        """Stopping after training is senseless. so the EvalHook
        after_train func is overwritten."""
        pass


class AIFLogging(EvalHook):
    """This hooks tries to log the metric through the AICore Tracking SDK."""
    nan_value = -100.

    def __init__(self, eval_period: int, get_last_eval_result_f: Callable):
        """Create instance of the hook.

        Parameters
        ----------
        eval_period: int
            This class is a subclass of the EvalHook and shares uses its way of
            trigering an evaluation to check for an early stop. The evaluation is
            simply triggered every 'eval_period' steps.
        get_last_eval_result_f: callable
            Function returning a dict with the last evaluation results or
            the value of the a specific metric directly.
            When combined with EvalHook it is probably advisable
            to retrieve its results and not to redo the evaluation.
            Check EarlyStoppingTrainer.build_hooks as an example.
        """
        super().__init__(eval_period, None)
        try:
            from sapai import tracking
        except ImportError:
            self.tracking_module = None
        else:
            self.tracking_module = tracking
        self.get_last_result = get_last_eval_result_f

    def _do_eval(self):
        if self.tracking_module is None:
            return
        new_result = self.get_last_result()
        if new_result is None:
            return
        metrics = self.format_metrics(new_result, self.trainer.iter + 1, [{'name': 'data_split', 'value': 'validation'}])
        self.tracking_module.log_metrics(metrics)

    @classmethod
    def nan_label(cls):
        return {'name': 'nans', 'value': f'{cls.nan_value}=nan'}

    @classmethod
    def format_metrics(cls, results, step, labels=[]):
        metrics = []
        for key, value in results.items():
            if not np.isfinite(value):
                value = cls.nan_value
                labels_i = [*labels] + [cls.nan_label()]
            else:
                labels_i = labels
            metric = {'name': key,
                      'value': value,
                      'step': step,
                      'labels': labels_i}
            metrics.append(metric)
        return metrics


class EarlyStop(Exception):
    """Exception used to trigger an early stop during the training."""
    pass


class EarlyStoppingTrainer(DefaultTrainer):
    """Default trainer. This is base trainer and cannot be used for trainer.
    Use ObjectDetectionTrainer, ImageClassificationTrainer and TripletDistanceTrainer
    for the actual trianing

    It includes multiple extentions in comparison to the detectron2.DefaultTrainer
    - Includes early stopping
    - AICore logging hook
    - Load best hook
    - Pop EvalHook from hook list when no test dataset was defined in the config
    - More augmentations configurable through the cfg
    """
    def build_hooks(self) -> List[HookBase]:
        """
        Build a list of default hooks, including timing, evaluation,
        checkpointing, lr scheduling, precise BN, writing events.

        Returns
        -------
        list[HookBase]
            List of hooks.
        """
        hooks = super().build_hooks()
        got_eval_hook = True
        if self.cfg.DATASETS.TEST is None or len(self.cfg.DATASETS.TEST) == 0:
            got_eval_hook = False
            eval_hook = None
            for i, h in enumerate(hooks):
                if isinstance(h, EvalHook) and not issubclass(type(h), EvalHook):
                    eval_hook = i
                    break
            if eval_hook is not None:
                del hooks[eval_hook]

        if not hasattr(self.cfg.SOLVER, 'EARLY_STOPPING'):
            raise ValueError('No `EARLY_STOPPING` node in config. Add the `Base-EarlyStopping` config to use the `EarlyStoppingTrainer`!')
        if got_eval_hook:
            if self.cfg.SOLVER.EARLY_STOPPING.LOAD_BEST:
                best_checkpoint_hook = BestCheckpointer(eval_period=self.cfg.TEST.EVAL_PERIOD,
                                                        checkpointer=self.checkpointer,
                                                        val_metric=self.cfg.SOLVER.EARLY_STOPPING.METRIC_NAME,
                                                        mode=self.cfg.SOLVER.EARLY_STOPPING.MODE,
                                                        file_prefix=self.cfg.SOLVER.EARLY_STOPPING.BEST_MODEL_PREFIX)
                hooks.append(best_checkpoint_hook)
            if self.cfg.SOLVER.EARLY_STOPPING.ENABLED:
                early_stopping_hook = EarlyStoppingHook(
                    eval_period=self.cfg.TEST.EVAL_PERIOD,
                    patience=self.cfg.SOLVER.EARLY_STOPPING.PATIENCE,
                    delta=self.cfg.SOLVER.EARLY_STOPPING.MIN_IMPROVEMENT,
                    mode=self.cfg.SOLVER.EARLY_STOPPING.MODE,
                    metric_name=self.cfg.SOLVER.EARLY_STOPPING.METRIC_NAME,
                    get_last_eval_result_f=lambda: getattr(self, '_last_eval_results', None))
                hooks.append(early_stopping_hook)
            if self.cfg.EVAL.LOG_METRICS:
                hooks.append(AIFLogging(eval_period=self.cfg.TEST.EVAL_PERIOD,
                                        get_last_eval_result_f=lambda: getattr(self, '_last_eval_results', None)))
        return [h for h in hooks if isinstance(h, HookBase)]

    def train(self):
        try:
            return super().train()
        except EarlyStop:
            if len(self.cfg.TEST.EXPECTED_RESULTS) and comm.is_main_process():
                assert hasattr(
                    self, "_last_eval_results"
                ), "No evaluation results obtained during training!"
                verify_results(self.cfg, self._last_eval_results)
                return self._last_eval_results

    @classmethod
    def build_train_loader(cls, cfg: CfgNode) -> 'torch.utils.data.DataLoader':
        raise NotImplementedError

    @classmethod
    def build_additional_augmentations(cls, cfg: CfgNode) -> List['T_.Transform']:
        """Build additional augmentations.

        Parameters
        ----------
        cfg: CfgNode
            Config

        Returns
        -------
        list of T_.Transform
            List of augmentation
        """
        augmentations = []
        if cfg.INPUT.get('RANDOM_LIGHTING', {}).get('ENABLED', False):
            augmentations.append(T_.RandomLighting(cfg.INPUT.RANDOM_LIGHTING.STRENGTH))
        if cfg.INPUT.get('RANDOM_BRIGHTNESS', {}).get('ENABLED', False):
            augmentations.append(T_.RandomBrightness(*cfg.INPUT.RANDOM_BRIGHTNESS.STRENGTH))
        if cfg.INPUT.get('RANDOM_SATURATION', {}).get('ENABLED', False):
            augmentations.append(T_.RandomSaturation(*cfg.INPUT.RANDOM_BRIGHTNESS.STRENGTH))
        if cfg.INPUT.get('RANDOM_CONTRAST', {}).get('ENABLED', False):
            augmentations.append(T_.RandomContrast(*cfg.INPUT.RANDOM_CONTRAST.STRENGTH))
        return augmentations


class ObjectDetectionTrainer(EarlyStoppingTrainer):
    """Object detection version of the EarlyStoppingTrainer.
    Default config: Base-EarlyStopping.yaml

    To make the trainer work for image classification the changer are:
    - 'build_evaluator' creates instance of ObjectDetectionEvaluator
    - 'build_train_loader' uses DatasetMapperWithAdditionalAugmentaions extending
    - 'build_test_loader' extends to default detectron2 build_test_loader func use
        bataching during evaluation.
    """
    @classmethod
    def build_evaluator(cls, cfg: CfgNode, _) -> 'ObjectDetectionEvaluator':
        return ObjectDetectionEvaluator(cfg)

    @classmethod
    def build_train_loader(cls, cfg: CfgNode) -> 'torch.utils.data.DataLoader':
        """Build train loader.
        The loder is the default loader from detectron2 but adds additional
        augementations. See build_additional_augmentations for details.

        Parameters
        ----------
        cfg: CfgNode
            Config

        Returns
        -------
        torch.utils.data.DataLoader
            Return the DataLoader for train data.
        """
        mapper = DatasetMapperWithAdditionalAugmentaions(cfg, is_train=True)  # pylint: disable=E1121, E1123, E1124, E1125
        return build_detection_train_loader(cfg, mapper=mapper)  # pylint: disable=E1121, E1123, E1124, E1125

    @classmethod
    def build_test_loader(cls, cfg: CfgNode, dataset_name: str):
        return build_detection_test_loader_batched(cfg, dataset_name)  # pylint: disable=E1121, E1123, E1124, E1125

class ImageClassificationTrainer(EarlyStoppingTrainer):
    """Image classification version of the EarlyStoppingTrainer.
    Default config: Base-EarlyStopping.yaml

    To make the trainer work for image classification the changer are:
    - 'build_evaluator' creates instance of ImageClassificationEvaluator
    - 'build_train_loader'/'build_test_loader' use DatasetMapperClassification
    """
    @classmethod
    def build_evaluator(cls, cfg: CfgNode, _) -> 'ImageClassificationEvaluator':
        return ImageClassificationEvaluator(cfg)

    @classmethod
    def build_train_loader(cls, cfg: CfgNode) -> 'torch.utils.data.DataLoader':
        mapper = DatasetMapperClassification(cfg, is_train=True)  # pylint: disable=E1121, E1123, E1124, E1125
        return build_classification_train_loader(cfg, mapper=mapper)  # pylint: disable=E1121, E1123, E1124, E1125

    @classmethod
    def build_test_loader(cls, cfg: CfgNode, dataset_name: Union[str, List[str]])  -> 'torch.utils.data.DataLoader':
        return build_classification_test_loader_batched(cfg, dataset_name)  # pylint: disable=E1121, E1123, E1124, E1125


class TripletDistanceTrainer(ImageClassificationTrainer):
    """Triplet distance learning version of the EarlyStoppingTrainer.
    Default config: Base-EarlyStopping.yaml
    In builds on top of the ImageClassificationTrainer because both use the same
    DataLoaders. Additional changes to make the trainer work for distance learning are:
    - 'build_evaluator' creates instance of ContrastiveEvaluator
    - 'build_hooks' it extends the EarlyStoppingTrainerHooks and adds PKTripletStrategySwitcher
        and PredictReservoirHook if needed for the sampler.
    """
    @classmethod
    def build_evaluator(cls, cfg: CfgNode, _) -> 'ContrastiveEvaluator':
        return ContrastiveEvaluator(cfg)

    def build_hooks(self) -> List[HookBase]:
        hooks = super().build_hooks()
        try:
            if isinstance(self.data_loader.batch_sampler, TripletReservoirSampler):
                hooks.append(PredictReservoirHook(self.data_loader.batch_sampler))
        except AttributeError:
            pass
        try:
            batch_sampler = self.data_loader.batch_sampler
            uses_triplet_strategy = False
            if isinstance(batch_sampler, PKTripletSampler):
                uses_triplet_strategy = True
                target = self.model
                strategies = self.cfg.DATALOADER.PK_SAMPLER.get('STRATEGY_SWITCHES', None)
            elif isinstance(batch_sampler, TripletReservoirSampler):
                uses_triplet_strategy = True
                target = batch_sampler
                strategies = self.cfg.DATALOADER.TRIPLET_RESERVOIR_SAMPLER.get('STRATEGY_SWITCHES', None)
        except AttributeError:
            pass
        else:
            if uses_triplet_strategy:
                if strategies is not None:
                    hook = PKTripletStrategySwitcher(strategies, target)
                    if len(hook.strategies) > 0:
                        hooks.append(hook)
        return hooks
