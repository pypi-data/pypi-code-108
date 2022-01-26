"""
A complete setup to train pytorch models in one file.
Makes use of simplepytorch.api for evaluation metrics and logging.

To create a model, just subclass TrainConfig.
"""
from os.path import dirname
from os import makedirs, symlink
from termcolor import colored
from tqdm import tqdm
from typing import Callable, Union, Dict, Tuple, Optional
import abc
import contextlib
import dataclasses as dc
import numpy as np
import random
import time
import torch as T

from simplepytorch import logging_tools, metrics


class Result(abc.ABC):
    """
    Accumulate and analyze results, for instance over the course of one epoch.

    This is an abstract base class, meant to be subclassed.

    `metrics` should be a list of class variables that store the results.
       For example, if metrics = ['precision'], there should be a class
       variable (or property) like `self.precision`.
    `update` should compute and store results for all listed metrics
    """
    @property
    def metrics(self) -> Tuple[str]:
        raise NotImplementedError('a list of metrics available in the result')

    def update(self, yhat, y, loss) -> None:
        """Compute and store results given:
          `yhat` - model predictions
          `y` - ground truth
          `loss` - training loss

          For example, for a classifier result, this function can store
          a confusion matrix.  Metrics can evaluate the precision, recall or
          matthew's correlation coefficient from the matrix.
        """
        raise NotImplementedError()

    # don't need to modify below here

    def __str__(self):
        return ", ".join(
            f'{colored(k, "cyan", None, ["bold"])}: {v:.5f}'
            for k, v in self.asdict().items()
            if not isinstance(v, (list, np.ndarray))
        )

    def __repr__(self):
        return f'<Result:{self.__class__.__name__}>'

    def asdict(self, prefix='') -> Dict[str, any]:
        """Fetch the stored metrics, and output a (flattened) dictionary"""
        tmp = {f'{prefix}{k}': getattr(self, k.lower().replace(' ', '_'))
               for k in self.metrics}
        rv = dict(tmp)
        # flatten any results of type dict, and prepend the prefix as needed.
        for tmp_key in tmp:
            if isinstance(tmp[tmp_key], dict):
                subdct = {f'{prefix}{k}': v for k,v in rv.pop(tmp_key).items()}
                assert not set(subdct.keys()).intersection(rv), 'code error: Result has nested dictionaries with overlapping keys'
                rv.update(subdct)
        return rv


def _get_log_data(cfg:'TrainConfig', cur_epoch:int, seconds:int, train_result: Result) -> dict:
    log_data = {'epoch': cur_epoch, 'seconds_training_epoch': seconds}
    log_data.update(train_result.asdict('train_'))
    if cfg.val_loader is not None:
        val_result = cfg.evaluate_perf(cfg, cfg.val_loader)
        log_data.update(val_result.asdict('val_'))
    if cfg.test_loader is not None:
        test_result = cfg.evaluate_perf(cfg, cfg.test_loader)
        log_data.update(test_result.asdict('test_'))
    return log_data


def _write_log_data(log_data:dict, data_logger:logging_tools.DataLogger):
    data_logger.writerow(log_data)
    data_logger.flush()
    # --> also log to console
    console_msg = [
        (f'{colored("epoch", "green", None, ["bold"])}: {log_data["epoch"]: 4d}'
         f', {colored("seconds_training_epoch", "green", None, ["bold"])}:'
         f' {log_data["seconds_training_epoch"]:1g}'),
    ]
    for spec, color in [('train', 'green'), ('val', 'yellow'), ('test', 'red')]:
        console_msg.extend([
            f'\n\t{colored(f"{spec.upper()} RESULTS: ", color, None, ["bold"])}',
            ', '.join([
                f'{colored(k, "cyan", None, ["bold"])}: {v: .5f}'
                for k, v in log_data.items()
                if k.startswith(f'{spec}_')
                and not isinstance(v, (np.ndarray, T.Tensor, list))]) ])
    print(''.join(console_msg))


def train(cfg: 'TrainConfig') -> None:
    data_logger = cfg.logger_factory(cfg)
    # save checkpoint before training (to save the initialization)
    if fp := cfg.checkpoint_if(cfg, None):
        cfg.save_checkpoint(save_fp=fp, cfg=cfg, cur_epoch=cfg.start_epoch)
    # record performance before training if start_epoch == 0
    if cfg.start_epoch == 0:
        # evaluate performance before any training.
        log_data = _get_log_data(
            cfg, cfg.start_epoch, np.nan,
            cfg.evaluate_perf(cfg, cfg.train_loader))
        _write_log_data(log_data, data_logger)
        cfg.start_epoch += 1
    # train model
    for cur_epoch in range(cfg.start_epoch, cfg.epochs + 1):
        with timer() as seconds:
            train_result = cfg.train_one_epoch(cfg)
        log_data = _get_log_data(cfg, cur_epoch, seconds(), train_result)
        _write_log_data(log_data, data_logger)
        if fp := cfg.checkpoint_if(cfg, log_data):
            cfg.save_checkpoint(save_fp=fp, cfg=cfg, cur_epoch=cur_epoch)

        #  if early_stopping(?):
        #      log.info("Early Stopping condition activated")
        #      break
    data_logger.close()


def train_one_epoch(cfg: 'TrainConfig') -> Result:
    cfg.model.train()
    result = cfg.result_factory()
    for minibatch in tqdm(cfg.train_loader, mininterval=1):
        X = minibatch[0].to(cfg.device, non_blocking=True)
        y = minibatch[1].to(cfg.device, non_blocking=True)
        cfg.optimizer.zero_grad()
        yhat = cfg.model(X)
        loss = cfg.loss_fn(yhat, y, *minibatch[2:])
        loss.backward()
        cfg.optimizer.step()
        with T.no_grad():
            result.update(yhat=yhat, y=y, loss=loss)
    return result


def evaluate_perf(cfg: 'TrainConfig', loader=None, result_factory=None) -> Result:
    if loader is None:
        loader = cfg.val_loader
    cfg.model.eval()
    with T.no_grad():
        result = cfg.result_factory() if result_factory is None else result_factory()
        for minibatch in tqdm(loader, mininterval=1):
            X = minibatch[0].to(cfg.device, non_blocking=True)
            y = minibatch[1].to(cfg.device, non_blocking=True)
            yhat = cfg.model(X)
            loss = cfg.loss_fn(yhat, y, *minibatch[2:])
            result.update(yhat=yhat, y=y, loss=loss)
    return result


def save_checkpoint(save_fp: str, cfg: 'TrainConfig', cur_epoch: int, save_model_architecture=True) -> None:
    state = {
        'random.getstate': random.getstate(),
        'np.random.get_state': np.random.get_state(),
        'torch.get_rng_state': T.get_rng_state(),
        'torch.cuda.get_rng_state': T.cuda.get_rng_state(cfg.device),

        'cur_epoch': cur_epoch,
    }
    if save_model_architecture:
        state.update({
            'model': cfg.model,
            'optimizer': cfg.optimizer
        })
    else:
        state.update({
            'model.state_dict': cfg.model.state_dict(),
            'optimizer.state_dict': cfg.optimizer.state_dict(),
        })

    makedirs(dirname(save_fp), exist_ok=True)
    T.save(state, save_fp)
    print("Checkpoint", save_fp)


@dc.dataclass
class TrainConfig:
    model: T.nn.Module
    optimizer: T.optim.Optimizer
    train_dset: T.utils.data.Dataset
    val_dset: Optional[T.utils.data.Dataset]
    test_dset: Optional[T.utils.data.Dataset]
    train_loader: T.utils.data.DataLoader
    val_loader: Optional[T.utils.data.DataLoader]
    test_loader: Optional[T.utils.data.DataLoader]
    loss_fn: Callable[[T.Tensor, T.Tensor], float]
    device: Union[T.device, str]
    epochs: int

    # Configure how to compute results.
    result_factory: Callable[[], Result]
    # You should make your own Result subclass.
    # ... or reference example configurations:
    #  result_factory = lambda: MultiLabelBinaryClassification(...)
    #  result_factory = lambda: MultiClassClassification(...)
    #  result_factory = lambda: SegmentationResult(
    #      classes=['tumor', 'infection', 'artifact'],
    #      model_final_layer=lambda x: (x > 0).long(),
    #      metrics=('mcc', 'loss', 'confusion_matrix'), )

    # Configure Checkpointing: choose when to checkpoint and where to save it
    #   when using the default train() function.
    #   The checkpoint function is evaluated in train() once before training
    #   starts and after every training epoch.  If it returns a filepath, save
    #   a checkpoint.
    #   Note: Before training starts, the log_data is None.  It is not None thereafter.
    # ... By default, checkpoint before training starts and after training ends
    checkpoint_if: Callable[('TrainConfig', Optional[dict]), Optional[str]] = (
        lambda cfg, log_data: (
            f'{cfg.base_dir}/checkpoints/epoch_0.pth'
                if (log_data is None and cfg.start_epoch == 0) else (
            f'{cfg.base_dir}/checkpoints/epoch_{cfg.epochs}.pth'
                if log_data is not None and log_data['epoch'] == cfg.epochs
            else None)))
    # ... other example checkpoint configurations:
    #  checkpoint_if = lambda cfg, log_data: None  # always disabled
    #  checkpoint_if = CheckpointBestOrLast(metric='val_acc', mode='max')  # checkpoint the best model historically and/or also final model

    # Configure logging.  By default, write to log rotated CSV with header
    # determined from the Result class and pre-configured train function.
    logger_factory: Callable[['TrainConfig'], logging_tools.DataLogger] = \
        lambda cfg: logging_tools.LogRotate(logging_tools.CsvLogger)(
            f'{cfg.base_dir}/perf.csv',
            ['epoch', 'seconds_training_epoch']
            + list(cfg.result_factory().asdict('train_'))
            + (list(cfg.result_factory().asdict('val_')) if cfg.val_loader is not None else [])
            + (list(cfg.result_factory().asdict('test_')) if cfg.test_loader is not None else []) )
    # alternative logger configurations.  Note: choice of what to log depends on metrics available in result_factory.
    #  logger_factory = lambda cfg: logging_tools.DoNothingLogger()
    #  logger_factory = lambda cfg: logging_tools.MultiplexedLogger(
    #      logging_tools.LogRotate(logging_tools.CsvLogger)(f'{cfg.base_dir}/perf.csv', ['epoch', 'seconds_training_epoch', 'train_loss', 'val_loss', ...]),
    #      logging_tools.LogRotate(logging_tools.HDFLogger)(f'{cfg.base_dir}/perf_tensors.h5', ['train_confusion_matrix', 'val_confusion_matrix']))

    experiment_id: str = 'debugging'
    start_epoch: int = 0  # if starts at 0, records performance before training.  if starts at 1, doesn't record performance before training.  this value is subsequently modified if loading from a checkpoint.
    train_one_epoch: Callable[['TrainConfig'], Result] = train_one_epoch
    evaluate_perf: Callable[['TrainConfig'], Result] = evaluate_perf
    save_checkpoint: Callable[[str, 'TrainConfig', int], None] = save_checkpoint
    train: Callable[['TrainConfig'], None] = train

    # stuff you probably don't want to configure

    @property
    def base_dir(self):
        return f'./results/{self.experiment_id}'


@contextlib.contextmanager
def timer():
    """Example:
        >>> with timer() as seconds:
            do_something(...)
        >>> print('elapsed time', seconds())
    """
    _seconds = []

    class seconds():
        def __new__(self):
            return _seconds[0]
    _tic = time.perf_counter()
    yield seconds
    _toc = time.perf_counter()
    _seconds.append(_toc - _tic)


class IsNextValueMonotonic:
    def __init__(self, mode='max'):
        self.mode = mode
        if mode == 'max':
            self._best_score = float('-inf')
            self._is_better = lambda x: x > self._best_score
        elif mode == 'min':
            self._best_score = float('inf')
            self._is_better = lambda x: x < self._best_score
        else:
            raise ValueError("Input mode is either 'min' or 'max'")

    def __call__(self, metric_value) -> bool:
        if self._is_better(metric_value):
            self._best_score = metric_value
            return True
        return False

class CheckpointBestOrLast:
    """
    Return a filepath to save checkpoints if:
        a) the model is best performing so far
        b) the current epoch equals the last epoch that should be trained

    This should be called at the end of an epoch during training.

        >>> fn = CheckpointBestOrLast('val_loss', mode='min',
                best_filename='best.pth',  # if not None, save checkpoint every time we get best loss.
                last_filename='epoch_{epoch}.pth',  # if not None, save checkpoint if the current epoch equals configured last epoch.
                )
        >>> fn(cfg, {'val_loss': 14.2})  # returns a filepath if model should be checkpointed
    """
    def __init__(self, metric: str, mode='max',
                 best_filename: Optional[str] = 'best.pth',
                 last_filename: Optional[str] = 'epoch_{epoch:03g}.pth'):
        """
        `metric` the name of a metric that will be available in log_data
        `mode` either 'max' or 'min' to maximize or minimize the metric value
        `best_filename` the filename (not filepath) where to save the
            checkpoint for the best performing model so far
        `last_filename` the filename (not filepath) where to save the
            checkpoint for the final state of model at end of training
            (not compatible with early stopping)

        The filenames, respectively, can be assigned None if you don't want to
        save a checkpoint for the best or last epoch.
        """
        self.metric = metric
        self.last_filename = last_filename
        self.best_filename = best_filename
        if best_filename is None:
            self._is_best_score_yet = lambda _: False
        else:
            self._is_best_score_yet = IsNextValueMonotonic(mode)

    def __call__(self, cfg: TrainConfig, log_data: Optional[Dict]) -> Optional[str]:
        """Return a filepath if a checkpoint should be saved"""
        if log_data is None:
            return
        is_best = self.best_filename is not None and self._is_best_score_yet(log_data[self.metric])
        is_last = self.last_filename is not None and log_data['epoch'] == cfg.epochs
        best_fp = (f'{{cfg.base_dir}}/checkpoints/{self.best_filename}').format(cfg=cfg, **log_data)
        last_fp = (f'{{cfg.base_dir}}/checkpoints/{self.last_filename}').format(cfg=cfg, **log_data)
        if is_last and is_best:
            makedirs(dirname(last_fp), exist_ok=True)
            symlink(best_fp, last_fp)
            return best_fp
        elif is_best:
            return best_fp
        elif is_last:
            return last_fp
        else:
            return


def load_checkpoint(fp: str, cfg: TrainConfig, load_random_state=True):
    """Update the model and optimizer in the given cfg.
    It's a mutable operation.  To make this point clear, don't return anything.
    """
    print('restoring from checkpoint', fp)
    S = T.load(fp, map_location=cfg.device)
    # random state and seeds
    if load_random_state:
        random.setstate(S['random.getstate'])
        np.random.set_state(S['np.random.get_state'])
        T.cuda.set_rng_state(S['torch.cuda.get_rng_state'].cpu(), cfg.device)
        T.random.set_rng_state(S['torch.get_rng_state'].cpu())
    # model + optimizer
    if 'model' in S:
        cfg.model = S['model']
    else:
        cfg.model.load_state_dict(S['model.state_dict'])
    cfg.model.to(cfg.device, non_blocking=True)
    if 'optimizer' in S:
        cfg.optimizer = S['optimizer']
    else:
        cfg.optimizer.load_state_dict(S['optimizer.state_dict'])
    cfg.start_epoch = S['cur_epoch']+1


@dc.dataclass
class SegmentationResult(Result):
    """
    Assume labels are a stack of one or more binary segmentation masks and report results independently per mask.

    Aggregate results, for instance over the course of an epoch. Aggregates
    per-pixel errors into a binary confusion matrix for each class (evaluating
    how well foreground and background are separated).

    It also records:
     - a confusion matrix for each task.
     - the total loss (sum)
     - the number of pixels processed
     - the number of images processed

    From each confusion matrix, the dice, accuracy and matthew's correlation
    coefficient are extracted.

        >>> res = SegmentationResult(
          classes=['tumor', 'infection', 'artifact'],
          model_final_layer=None  # function to modify the given model predictions before computing confusion matrix.
          metrics=('mcc', 'acc', 'dice', 'loss', 'num_images', 'confusion_matrix', )  # ... or 'combined_confusion_matrix')
        )
        >>> res.update(yhat, y, loss)
        >>> res.asdict()  # a flattened dict of results.  For each dict key defined in `metrics`, get a value.  If value is itself a dict, merge (flatten) it into existing results.

        yhat and y should have shape (B,C,H,W) where C has num channels.  loss is a scalar tensor.
    """
    # adjustable parameters
    classes: Tuple[str] = ('',)  # e.g. ['tumor', 'infection', 'artifact']
    model_final_layer: Union[T.nn.Module, Callable[[T.Tensor], T.Tensor]] = None
    metrics: Tuple[str] = ('mcc', 'acc', 'dice', 'loss', 'num_images', 'confusion_matrix')  #'combined_confusion_matrix')

    # parameters you probably shouldn't adjust
    _cms: Dict[str, T.Tensor] = dc.field(init=False)
    loss: float = 0
    num_images: int = 0

    def __post_init__(self):
        self._cms = {k: T.zeros((2,2), dtype=T.float)
                     for k in self.classes}

    def update(self,
               yhat: T.Tensor,
               y: T.Tensor,
               loss: T.Tensor,
               ):
        assert len(self.classes) == yhat.shape[1] == y.shape[1]

        self.loss += loss.item()
        self.num_images += yhat.shape[0]
        # change yhat to predict class indices
        if self.model_final_layer is not None:
            yhat = self.model_final_layer(yhat)

        # update confusion matrix
        yhat = yhat.permute(0,2,3,1)
        y = y.permute(0,2,3,1)
        device = y.device
        assert len(self.classes) == y.shape[-1], 'sanity check'
        assert len(self.classes) == yhat.shape[-1], 'sanity check'
        for i,kls in enumerate(self.classes):
            self._cms[kls] = self._cms[kls].to(device, non_blocking=True) + metrics.confusion_matrix(
                yhat=yhat[...,i].reshape(-1),
                y=y[...,i].reshape(-1),
                num_classes=2)

    @property
    def dice(self) -> Dict[str,float]:
        ret = {}
        for kls in self.classes:
            cm = self._cms[kls]
            (_, fp), (fn, tp) = (cm[0,0], cm[0,1]), (cm[1,0], cm[1,1])
            ret[f'dice_{kls}'] = (2*tp / (tp+fp + tp+fn)).item()
        return ret

    @property
    def mcc(self) -> Dict[str,float]:
        return {
            f'mcc_{k}': metrics.matthews_correlation_coeff(
                self._cms[k]).cpu().item() for k in self.classes}

    @property
    def acc(self) -> Dict[str,float]:
        return {
            f'acc_{k}': metrics.accuracy(cm).item()
            for k,cm in self._cms.items()}

    @property
    def confusion_matrix(self) -> Dict[str, np.ndarray]:
        return {f'cm_{k}': self._cms[k].cpu().numpy() for k in self.classes}

    @property
    def combined_confusion_matrix(self) -> np.ndarray:
        """ Convert self.confusion_matrices into a flat matrix.  Useful for logging and simpler data storage"""
        tmp = T.cat([self._cms[k] for k in self.classes]).cpu().numpy()
        # add the class names for each confusion matrix as a column
        tmp = np.column_stack(np.repeat(self.classes, tmp.shape[0]), tmp)
        return tmp


@dc.dataclass
class ClassifierResult(Result):
    """
    Aggregate results, for instance over the course of an epoch and maintain a
    confusion matrix.

    DEPRECATED: Suggested to use this instead:  MultiLabelBinaryClassification(...)

    It computes a confusion matrix of the epoch, and also records
     - the total loss (sum)
     - the number of samples processed.

    From the confusion matrix, the accuracy and matthew's correlation
    coefficient are extracted.

        >>> res = ClassifierResult(
          num_classes=2,  # for binary classification
          model_final_layer=None,  # function to modify the given model predictions before confusion matrix.
          metrics=('mcc', 'acc', 'loss', 'num_samples', 'confusion_matrix')  # define what values are output by asdict()
        )
        >>> res.update(yhat, y, loss, minibatch_size)
        >>> res.asdict()  # Dict[str:Any]  Returns the MCC, ACC, Loss, Num Samples and Confusion Matrix.

        yhat and y each have shape (B,C) for B samples and C classes.
    """
    # params you can adjust
    num_classes: int
    model_final_layer: Union[T.nn.Module, Callable[[T.Tensor], T.Tensor]] = None
    metrics = ('mcc', 'acc', 'loss', 'num_samples', 'confusion_matrix')  # define what values are output by asdict()

    # params you probably shouldn't adjust
    _confusion_matrix: T.Tensor = dc.field(init=False)  # it is updated to tensor.
    loss: float = 0
    num_samples: int = 0

    def __post_init__(self):
        self._confusion_matrix = T.zeros(self.num_classes, self.num_classes)

    def update(self, yhat: T.Tensor, y: T.Tensor, loss: T.Tensor):
        minibatch_size = y.shape[0]
        # update loss
        self.loss += loss.item()
        self.num_samples += minibatch_size
        # change yhat (like apply softmax if necessary)
        if self.model_final_layer is not None:
            yhat = self.model_final_layer(yhat)
        # update confusion matrix
        self._confusion_matrix = self._confusion_matrix.to(y.device, non_blocking=True)
        self._confusion_matrix += metrics.confusion_matrix(yhat=yhat, y=y, num_classes=self.num_classes)
        assert np.allclose(self._confusion_matrix.sum().item(), self.num_samples), 'sanity check'

    @property
    def mcc(self) -> float:
        return metrics.matthews_correlation_coeff(self._confusion_matrix).item()

    @property
    def acc(self) -> float:
        return metrics.accuracy(self._confusion_matrix).item()
        #  return (self._confusion_matrix.trace() / self._confusion_matrix.sum()).item()

    @property
    def confusion_matrix(self) -> np.ndarray:
        return self._confusion_matrix.cpu().numpy()


class MultiClassClassification(Result):
    """A result class for Multi-Class Classification.
    Maintains a confusion matrix.

    This class is useful to to aggregate results, for instance over the course
    of an epoch.
    """
    @property
    def metrics(self):
        metrics = ('Loss', 'Num Samples', 'MCC', 'Acc', 'BAcc', 'cm')
        if self._cm.shape[0] == 2:
            metrics += ('Precision', 'Recall', 'F1', )
            # exclude these since we haven't determined if micro or macro avg or other
        return metrics

    def __init__(self, num_classes:int,
                 binarize_fn:Callable[T.Tensor,T.Tensor]=None):
        """
        Args:
            num_classes:  a list of binary outcomes predicted by the model.
            binarize_fn:  optional function or pytorch module to compute
                binarized predictions `yhat = binarize(model(x))`.  This is
                evaluated before computing the confusion matrix.
                For instance, `binarize_fn=(lambda yh: T.sigmoid(yh)>.5)`.
        """
        self._cm = T.zeros((num_classes, num_classes))
        self._binarize_fn = (lambda x: x) if binarize_fn is None else binarize_fn
        self.loss = 0
        self.num_samples = 0

    @property
    def acc(self):
        """Accuracy"""
        return metrics.accuracy(self._cm).item()

    @property
    def bacc(self):
        """Balanced Accuracy"""
        return metrics.balanced_accuracy(self._cm).item()

    @property
    def mcc(self):
        """Matthew's Correlation Coefficient"""
        return metrics.matthews_correlation_coeff(self._cm).item()

    @property
    def f1(self):
        return metrics.f1_score(self._cm).item()

    @property
    def precision(self):
        return metrics.precision(self._cm).item()

    @property
    def recall(self):
        return metrics.recall(self._cm).item()

    @property
    def cm(self):
        """Output the binary confusion matrix"""
        return self._cm.numpy().tolist()

    def update(self, yhat, y, loss) -> None:
        """Compute and store results given:
          `yhat` - model predictions
          `y` - ground truth
          `loss` - training loss

          For example, for a classifier result, this function can store
          a confusion matrix.  Metrics can evaluate the precision, recall or
          matthew's correlation coefficient from the matrix.
        """
        self.num_samples += yhat.shape[0]
        self.loss += loss.item()
        binarized = self._binarize_fn(yhat)
        if y.ndim == 2:
            assert y.shape[1] == 1, 'sanity check: y should be a scalar number per observation.'
            y = y.squeeze(1)
        assert y.shape == (yhat.shape[0], ), f'sanity check {y.shape} == {yhat.shape[0]}'
        assert y.dtype == binarized.dtype == T.long, 'sanity check'
        assert yhat.shape[1] >= y.max(), 'sanity check'
        self._cm += metrics.confusion_matrix(
            y, binarized, num_classes=self._cm.shape[0]).cpu()


class MultiLabelBinaryClassification(Result):
    """A result class for Multi-Label Binary Classification.
    Maintains one binary confusion matrix for each class and computes
    classification metrics from them.

    This class is useful to to aggregate results, for instance over the course
    of an epoch.
    """
    metrics = ('Loss', 'Num Samples', 'MCC', 'Precision', 'Recall', 'F1', 'Acc', 'BAcc', 'cm')

    def __init__(self, class_names:tuple,
                 binarize_fn:Callable[T.Tensor,T.Tensor]=None,
                 report_avg:bool=False):
        """
        Args:
            class_names:  a list of binary outcomes predicted by the model.
            binarize_fn:  optional function or pytorch module to compute
                binarized predictions `yhat = binarize(model(x))`.  This is
                evaluated before computing the confusion matrix.
                For instance, `binarize_fn=(lambda yh: T.sigmoid(yh)>.5)`.
            report_avg:  If True, also compute the average of each metric
                across all classes.
        """
        self._cms = {i: T.zeros((2,2)) for i in class_names}
        self._binarize_fn = (lambda x: x) if binarize_fn is None else binarize_fn
        self.loss = 0
        self.num_samples = 0
        self.report_avg = report_avg

    @property
    def acc(self):
        """Accuracy"""
        return self._on_each_cm('Acc {class_name}', metrics.accuracy)

    @property
    def bacc(self):
        """Balanced Accuracy"""
        return self._on_each_cm('BAcc {class_name}', metrics.balanced_accuracy)

    @property
    def mcc(self):
        """Matthew's Correlation Coefficient"""
        return self._on_each_cm('MCC {class_name}', metrics.matthews_correlation_coeff)

    @property
    def f1(self):
        return self._on_each_cm('F1 {class_name}', metrics.f1_score)

    @property
    def precision(self):
        return self._on_each_cm('Precision {class_name}', metrics.precision)

    @property
    def recall(self):
        return self._on_each_cm('Recall {class_name}', metrics.recall)

    @property
    def cm(self):
        """Output the binary confusion matrices"""
        return {f'cm {class_name}': cm.numpy().tolist()
                for class_name, cm in self._cms.items()}

    def _on_each_cm(self, metric_name, fn):
        rv = {}
        avg = 0
        for kls, cm in self._cms.items():
            val = fn(cm).item()
            rv[metric_name.format(class_name=kls)] = val
            avg += val/len(self._cms)
        if self.report_avg:
            rv[metric_name.format(class_name='AVG')] = avg
        return rv

    def update(self, yhat, y, loss) -> None:
        """Compute and store results given:
          `yhat` - model predictions
          `y` - ground truth
          `loss` - training loss

          For example, for a classifier result, this function can store
          a confusion matrix.  Metrics can evaluate the precision, recall or
          matthew's correlation coefficient from the matrix.
        """
        self.num_samples += yhat.shape[0]
        self.loss += loss.item()
        assert yhat.shape == y.shape
        assert yhat.ndim == 2 and yhat.shape[1] == len(self._cms), "sanity check: model outputs expected prediction shape"
        binarized = self._binarize_fn(yhat)
        assert binarized.dtype == T.long, 'sanity check binarize fn'
        assert binarized.shape == y.shape, 'sanity check binarize fn'
        for i, (kls, cm) in enumerate(self._cms.items()):
            cm += metrics.confusion_matrix(y[:, i], binarized[:, i], num_classes=2).cpu()
