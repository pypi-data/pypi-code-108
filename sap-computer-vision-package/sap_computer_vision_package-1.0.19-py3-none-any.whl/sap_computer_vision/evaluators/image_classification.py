from typing import Dict, Union, List
import itertools
import logging

import torch
import numpy as np
from detectron2.config import configurable, CfgNode
import detectron2.utils.comm as comm


logger = logging.getLogger(__name__)


class ImageClassificationEvaluator:
    """Detectron2 compatible evaluator to get metrics for image classification use cases

    The metrics are calculated using function get_metrics.
    See its documentation for details.
    """
    @configurable
    def __init__(self, beta=1.0, multi_label=False, distributed=False, class_names=None):
        """Create Evaluator instance. This class is intended to be used by the trainer.

        To manually determine metrics it is easier to use the get_metrics function directly.

        Parameters
        ----------
        beta: float
            F1 score beta.
        multi_label: bool, optional, default=True
            This is just a placeholder. Evaluation of for multi_label predictions
            is not yet implemented!
        class_names: None or list of str, optinal, default=None
            Class id to str mapping. If provided the results
            will be 'accuracy:<class_name>' instead of
            'accuracy:<class_id>'.
        distributed: bool, optional, default=False
            WARNING: not tested
            In principal this evaluator can be used in a distributed training
            scenario.
        """
        self._beta = beta
        self._class_names = None
        self._distributed = distributed
        self._multi_label = multi_label
        self._class_names = class_names
        self.reset()

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
        return {'beta': cfg.EVAL.IMAGE_CLASSIFICATION.BETA,
                'distributed': cfg.SOLVER.REFERENCE_WORLD_SIZE > 0,
                'multi_label': cfg.MODEL.IMAGE_CLASSIFIER.MULTI_LABEL,
                'class_names': cfg.get('TRAINING_INFO', {}).get('THING_CLASSES', None)
                }

    def process(self, inputs, outputs):
        """Function called by the trainer after each prediction step.

        This functions stores all relevant results.

        Parameters
        ----------
        inputs: dict
            Model input dict

        outputs: torch.Tensor
            Model output (logits)
        """
        if self.n_classes is None:
            self.n_classes = outputs.size()[1]
            if self._class_names is not None:
                if len(self._class_names) != self.n_classes:
                    logger.warning('The provided class names and output.size mus be same length.')
                    self._class_names = None
        for inp, out in zip(inputs, outputs):
            if self._multi_label:
                raise NotImplementedError
            else:
                truth = inp['class_id']
                predicted = int(torch.argmax(out))
                self._predictions.append(predicted)
                self._truth.append(truth)

    def reset(self):
        """Reset all stored results."""
        self._predictions = []
        self._truth = []
        self.n_classes = None

    def evaluate(self) -> Dict[str, float]:
        """Evaluate based on stored results.

        Returns
        -------
        dict
            Dict containing metrics.
        """
        if self._distributed:
            comm.synchronize()
            predictions = comm.gather(self._predictions, dst=0)
            predictions = list(itertools.chain(*predictions))
            truth = comm.gather(self._truth, dst=0)
            truth = list(itertools.chain(*truth))
            if not comm.is_main_process():
                return
        else:
            predictions = self._predictions
            truth = self._truth
        if self._multi_label:
            raise NotImplementedError
        else:
            return get_metrics(predictions,
                               truth,
                               beta=self._beta,
                               class_names=self._class_names,
                               return_confusion_matrix=False)


def get_metrics(predictions: 'np.array',
                truth,
                beta: float=1.0,
                return_confusion_matrix: bool=True,
                class_names: Union[None, List[str]]=None):
    """"Function to calculate metrics for image classification.

    For giving predictions and true labels vales accuracies, recall values and F1 scores
    are calculated for every class individually and all classes combined.

    Parameters
    ----------
    predictions: np.array(feat_dim) of int
        Predicted class id.
    truth: np.array(n) of ints
        True class id.
    beta: float, optional, default=1.0
        F1 score beta.
    return_confusion_matrix: bool, optinal, default=True
        Return confusion matrix.
    class_names: None or list of str, optinal, default=None
        Class id to str mapping. If provided the results
        will be 'accuracy:<class_name>' instead of
        'accuracy:<class_id>'.

    Returns
    ----------
    dict(str, float)
       Dictionary with the different metrics
    """
    if class_names is None:
        n_classes = len(np.unique(truth))
        class_names = [str(i) for i in range(n_classes)]
    else:
        n_classes = len(class_names)
    confusions = np.zeros((n_classes, n_classes), dtype=np.int32)
    for t, p in zip(truth, predictions):
        confusions[t, p] += 1
    results = {}
    results['accuracy'] = np.sum(np.diag(confusions)) / np.sum(confusions)
    for i, n in enumerate(class_names):
        precision = confusions[i, i] / np.sum(confusions[i, :])
        recall = confusions[i, i] / np.sum(confusions[:, i])
        results[f'accuracy:{n}'] = precision
        results[f'recall:{n}'] = recall
        results[f'f1score:{n}'] = (1+beta)**2 * (precision * recall) / ((beta**2 * precision) + recall)
    if return_confusion_matrix:
        results['confusions'] = confusions.copy()
    return results
