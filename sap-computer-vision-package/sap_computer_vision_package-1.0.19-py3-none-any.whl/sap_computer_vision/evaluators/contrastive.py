from typing import NoReturn, Union, Iterable, NoReturn, Dict
import itertools

import torch
import numpy as np
from detectron2.config import configurable
from scipy.spatial.distance import pdist, cdist, squareform
import detectron2.utils.comm as comm
from detectron2.config import CfgNode


class ContrastiveEvaluator:
    """Detectron2 compatible evaluator to get metrics for triplet distance learning.

    The metrics are calculated using function get_metrics.
    See its documentation for details.
    """
    @configurable
    def __init__(self, ks: Union[None, Iterable[int]]=None, metric='euclidean', metric_kwargs={}, distributed=False):
        """Create Evaluator instance. This class is intended to be used by the trainer.

        To manually determine metrics it is easier to use the get_metrics function directly.

        Parameters
        ----------
        ks: None or iterable of ints, optional, default=None
            Different k values used in the evaluation.
            The values have to be > 0.
        metric: str, optional, default=None
            Metric used during evaluation to determine the distance between embeddings.
            Check get_metrics for details.
        metric_kwargs: dict, optional, default={}
            kwargs passed to scipy.spatial.distance.pdist/ddist
            Check get_metrics for details.
        distributed: bool, optional, default=False
            WARNING: not tested
            In principal this evaluator can be used in a distributed training
            scenario.
        """
        if ks is None:
            ks = [1, 2, 3]
        self._ks = ks
        self._metric = metric
        self._metric_kwargs = {} if metric_kwargs is None else metric_kwargs
        self._distributed = distributed
        self._cpu_device = torch.device("cpu")
        self.reset()

    def process(self, inputs: Dict, outputs: 'torch.Tensor') -> NoReturn:
        """Function called by the trainer after each prediction step.

        This functions stores all relevant results.

        Parameters
        ----------
        inputs: dict
            Model input dict

        outputs: torch.Tensor
            Embeddings calculated by the model.
        """
        self._labels.extend([inp['class_id'] for inp in inputs])
        self._embeddings.extend(outputs.to(self._cpu_device).tolist())

    @classmethod
    def from_config(cls, cfg: 'CfgNode') -> Dict:
        """Classmethod to create an instance based on the config.

        Check detectron configs mechanism.

        Parameters
        ----------
        cfg: CfgNode
            Config

        Returns
        -------
        dict
            Dict with the relevant kwargs. This dict can be consumed by the
            __init__ function.
        """
        attr = {'ks': cfg.EVAL.CONTRASTIVE.TOP_KS,
                'metric': cfg.EVAL.CONTRASTIVE.METRIC,
                'metric_kwargs': cfg.EVAL.CONTRASTIVE.get('METRIC_KWARGS', {}),
                'distributed': cfg.SOLVER.REFERENCE_WORLD_SIZE > 0,}
        return attr

    def reset(self) -> NoReturn:
        """Reset all stored results."""
        self._embeddings = []
        self._labels = []

    def evaluate(self) -> Dict[str, float]:
        """Evaluate based on stored results.

        Returns
        -------
        dict
            Dict containing metrics.
        """
        if self._distributed:
            comm.synchronize()
            embeddings = comm.gather(self._embeddings, dst=0)
            embeddings = list(itertools.chain(*embeddings))
            labels = comm.gather(self._labels, dst=0)
            labels = list(itertools.chain(*labels))
            if not comm.is_main_process():
                return
        else:
            embeddings = self._embeddings
            labels = self._labels
        embeddings = np.array(embeddings)
        labels = np.array(labels)
        return get_metrics(embeddings, labels, ks=self._ks, metric=self._metric, **self._metric_kwargs)


def _get_mask(label_i: 'np.array', labels: 'np.array') -> 'np.array':
    mask = labels == label_i
    n = np.sum(mask)
    return mask, n


def get_metrics(embeddings: 'np.array',
                labels: 'np.array',
                index_embeddings: Union[None, 'np.array']=None,
                index_labels: Union[None, 'np.array']=None,
                ks: Union[None, Iterable[int]]=None,
                metric: str='euclidean',
                **metric_kwargs) -> Dict[str, float]:
    """"Function to calculate metrics for contrastive/distance learning applications.

    For giving embeddings and labels the `top_k_accuracy`, `rank_rate_k` and `mean_dist_pos/neg` are calculated.

    top_k_accuracy:
        For every test case it is check of an example of the same class is within the top k results.
        If it is the case this is counted as 1 and if not as 0. For the accuracy the counts are devided
        by the number of tests.

    rank_rate_k:
        For every test case the index/rank `r` of the nearest neighbor of the same class is determined.
        The ranks starts with 0. If there is no example of the same class among the k closest neighbors
        r=k. With thoses ranks the mean of (k-r) / k is calcuated.

    mean_dist_pos/mean_dist_neg:
        For every test_case the mean distance to examples of the same class and to examples of all other
        classes is calculated. Those distances are average and returned.

    To calculate distance metrics scipy.distance.pdist/cdist are used.

    Parameters
    ----------
    embeddings: np.array(n, feat_dim) of floats
        Embeddings vector for the test cases.
    labels: np.array(n) of ints
        Label ids to determine positive/negative examples.
    index_embeddings: None or np.array(m, feat_dim) of floats, optional, default=None
        Embeddings vector for the index cases.
        If none the for every test case the n-1 remaing test cases are used as the index.
    index_labels: None or np.array(m) of ints, optional, default=None
        Label ids to determine positive/negative examples.
    ks: Iterable(int), optional, default=None
        Different `k` values used to calculate the rank rate and the accuracy.
        If `None` [1, 3, 5, 10] is used.
    metric: str, optional, default='euclidean'
        Metric used to calculate the distance. For distance calculations
        scipy.distance.pdist/cdist are being used. See scipy documentation for
        vailable options.
    **metric_kwargs
        All other keyword arguments are passed to the scipy.distance.pdist/cdist
        functions. See scipy documentation for
        vailable options.

    Returns
    ----------
    dict(str, float)
       Dictionary with the different metrics

    Raises
    ------
    ValueError
        If `index_embeddigns` and `index_labels` have different length.
    """
    if ks is None:
        ks = [1, 3, 5, 10]

    metrics = {**{f'top_{k}_acc': 0 for k in ks}, **{f'rank_rate_{k}': 0 for k in ks}}

    if index_embeddings is None:
        expanded_matrix = squareform(pdist(embeddings, metric=metric, **metric_kwargs))
        index_labels = labels
        min_n = 2
    else:
        expanded_matrix = cdist(embeddings, index_embeddings, metric=metric, **metric_kwargs)
        if index_labels is None or len(index_labels) != len(index_embeddings):
            raise ValueError("When using `index_embeddings` `index_labels` with the same length "
                             "must be provided to the function")
        min_n = 1

    cls_masks = {}
    dists_pos = []
    dists_neg = []
    tested = 0
    for i, l_i in enumerate(labels):
        cls_mask, n = cls_masks.setdefault(l_i, _get_mask(l_i, index_labels))
        if n < min_n:
            continue
        tested += 1
        dists_neg.append(np.mean(expanded_matrix[i, np.logical_not(cls_mask)]))
        dists_pos.append(np.mean(expanded_matrix[i, cls_mask]))
        order = np.argsort(expanded_matrix[i, :])
        if index_embeddings is None:
            dists_pos[-1] *= n/(n-1)
            order = np.delete(order, np.where(order == i)[0])
        for k in ks:
            metrics[f'top_{k}_acc'] += 1 if l_i in index_labels[order[:k]] else 0
            positions = np.where(index_labels[order[:k]] == l_i)[0]
            if len(positions) == 0:
                metrics[f'rank_rate_{k}'] += 0.
            else:
                metrics[f'rank_rate_{k}'] += (k - positions[0]) / k
    for k in ks:
        metrics[f'top_{k}_acc'] /= tested
        metrics[f'rank_rate_{k}'] /= tested
    metrics['mean_dist_pos'] = np.mean(dists_pos)
    metrics['mean_dist_neg'] = np.mean(dists_neg)
    return metrics
