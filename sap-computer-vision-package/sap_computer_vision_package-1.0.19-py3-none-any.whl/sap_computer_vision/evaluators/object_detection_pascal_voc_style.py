import logging
from collections import defaultdict, namedtuple
import itertools
from typing import Dict, Iterable, List, Any, Union

import numpy as np
import torch
from detectron2.data import DatasetCatalog
import detectron2.utils.comm as comm
from detectron2.structures import Boxes, pairwise_iou
from detectron2.modeling.matcher import Matcher
from detectron2.config import configurable, CfgNode
from detectron2.structures import Instances

DetectionBox = namedtuple('DetectionBox', ['image_id', 'score', 'cls', 'xmin', 'ymin', 'xmax', 'ymax'])


class ObjectDetectionEvaluator:
    """Detectron2 compatible evaluator to get metrics for image classification use cases

    The metrics are calculated using function get_metrics.
    See its documentation for details.
    """
    @configurable
    def __init__(self,
                 dataset_names: Iterable[str],
                 thresholds=None,
                 min_iou_for_hit=0.5,
                 box_overlap_cut=None,
                 box_overlap_keep='biggest',
                 ignore_labels_for_overall_performance=False,
                 class_names=None,
                 distributed: bool=False):
        """Create Evaluator instance. This class is intended to be used by the trainer.

        To manually determine metrics it is easier to use the get_metrics function directly.

        Parameters
        ----------
        dataset_names: None or iterable of ints, optional, default=None
            Different k values used in the evaluation.
            The values have to be > 0.
        thresholds: None or np.array of floats
            Confidence cuts used to calculate the mAP.
            If None the default thresholds are used.
        min_iou_for_hit: float, optional, default=0.5
            Min iou (intersection over union) for a predicted bbox and a true bbox to be
            considered a hit.
        box_overlap_cut: None or float, optional, default=None
            Optional cut to reject overlapping predictions.
            If 'None' no cut is applied.
        box_overlap_keep: str, optional, default='biggest'
            When applying a cut for overlapping boxex the 'biggest'
            or 'biggest' bbox or the bbox with the 'highest_score'
            will be kept.
        ignore_labels_for_overall_performance: bool, optional, default=False
            If True the label of bbox are ignored when calculating
            the overall performance.
        class_names: None or list of str, optinal, default=None
            Class id to str mapping. If provided the results
            will be 'mAP:<class_name>' instead of
            'mAP:<class_id>'.
        distributed: bool, optional, default=False
            WARNING: not tested
            In principal this evaluator can be used in a distributed training
            scenario.
        """
        self._min_iou_for_hit = min_iou_for_hit
        self._box_overlap_cut = box_overlap_cut
        self._box_overlap_keep = box_overlap_keep
        self._ignore_labels_for_overall_performance = ignore_labels_for_overall_performance
        self._thresholds = thresholds
        self._distributed = distributed
        self._cpu_device = torch.device("cpu")
        self._logger = logging.getLogger(__name__)
        self._ground_truth = {}
        self._class_names = class_names
        for dataset_name in dataset_names:
            self._dataset_name = dataset_name
            self._ground_truth = {**self._ground_truth, **{v['image_id']: v for v in DatasetCatalog.get(dataset_name)}}
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
        attr = {'dataset_names': cfg.DATASETS.TEST,
                'distributed': cfg.SOLVER.REFERENCE_WORLD_SIZE > 0,
                'thresholds': cfg.EVAL.OBJECT_DETECTION.THRESHOLDS,
                'min_iou_for_hit': cfg.EVAL.OBJECT_DETECTION.MIN_IOU_FOR_HIT,
                'box_overlap_cut': cfg.EVAL.OBJECT_DETECTION.BOX_OVERLAP_CUT,
                'box_overlap_keep': cfg.EVAL.OBJECT_DETECTION.BOX_OVERLAP_KEEP,
                'ignore_labels_for_overall_performance': cfg.EVAL.OBJECT_DETECTION.IGNORE_CLASS_LABELS_FOR_OVERALL_PERFORMANCE,
                'class_names': cfg.get('TRAINING_INFO', {}).get('THING_CLASSES', None)}
        return attr

    def reset(self):
        """Reset all stored results."""
        self._predictions = {}

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
        for input, output in zip(inputs, outputs):
            image_id = input["image_id"]
            if "instances" not in output.keys():
                raise ValueError('`output` does not contain `instances`. Probably the model is not an '
                                 'object detection model outputting bounding boxes.')
            instances = output["instances"].to(self._cpu_device)
            if image_id in self._predictions:
                raise RuntimeError('`image_id` appeared twice!')

            self._predictions[image_id] = instances

    def evaluate(self):
        """Evaluate based on stored results.

        Returns
        -------
        dict
            Dict containing metrics.
        """
        if self._distributed:
            comm.synchronize()
            _predictions = comm.gather(self._predictions, dst=0)
            _predictions = list(itertools.chain(*_predictions))
            _ground_truth = comm.gather(self._ground_truth, dst=0)
            _ground_truth = list(itertools.chain(*_ground_truth))

            if not comm.is_main_process():
                return
        else:
            _predictions = self._predictions
            _ground_truth = self._ground_truth

        ground_truth = []
        predictions = []
        for img_id, prediction in _predictions.items():
            ground_truth.append(self._ground_truth[img_id])
            predictions.append(prediction)
        results = evaluate_box_proposals(predictions,
                                         ground_truth,
                                         thresholds=self._thresholds,
                                         min_iou_for_hit=self._min_iou_for_hit,
                                         pred_box_overlap_threshold=self._box_overlap_cut,
                                         keep_overlapping_box=self._box_overlap_keep,
                                         ignore_class_label_for_overall_performance=self._ignore_labels_for_overall_performance,
                                         class_names=self._class_names)
        return results


def evaluate_box_proposals(predictions: List[Instances],
                           ground_truth: List[Dict[str, Any]],
                           thresholds: Union[None, 'np.array']=None,
                           min_iou_for_hit: float=0.5,
                           pred_box_overlap_threshold: Union[None, float]=None,
                           keep_overlapping_box: str='biggest',
                           ignore_class_label_for_overall_performance: bool=False,
                           add_curve_points: bool=False,
                           class_names: Union[None, List[str]]=None):
    """Create Evaluator instance. This class is intended to be used by the trainer.

    To manually determine metrics it is easier to use the get_metrics function directly.
    Parameters
    ----------
    predictions: list of detectron2.structures.Instances
        List of model predictions. The model predictions are of type
        Instances. Those Instances should have values for
        "pred_boxes", "pred_classes", "scores".
    ground_truth: list of dicts
        List of grouth truths. The dicts are detectron2's lightweight
        dict formats of the datasets. It is return format of
        DatasetCatalog.get(dataset_name).
    thresholds: None or np.array of floats
        Confidence cuts used to calculate the mAP.
        If None the default thresholds are used [0.05, 0.1, ... 0.95].
    min_iou_for_hit: float, optional, default=0.5
        Min iou (intersection over union) for a predicted bbox and a true bbox to be
        considered a hit.
    pred_box_overlap_threshold: None or float, optional, default=None
        Optional cut to reject overlapping predictions.
        If 'None' no cut is applied.
    keep_overlapping_box: str, optional, default='biggest'
        When applying a cut for overlapping boxex the 'biggest'
        or 'biggest' bbox or the bbox with the 'highest_score'
        will be kept.
    ignore_class_label_for_overall_performance: bool, optional, default=False
        If True the label of bbox are ignored when calculating
        the overall performance.
    add_curve_points: bool, optional, default=False
        If True the individual points from the mAP calculation are added to the
        return dict.
    class_names: None or list of str, optinal, default=None
        Class id to str mapping. If provided the results
        will be 'mAP:<class_name>' instead of
        'mAP:<class_id>'.
    """
    pred_box_overlap_threshold = None if not isinstance(pred_box_overlap_threshold, float) else pred_box_overlap_threshold
    if not thresholds:
        thresholds = np.arange(0.05, 0.95+1e-5, 0.05)
    scores = defaultdict(lambda: defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0}))
    for prediction, gt in zip(predictions, ground_truth):
        gt_boxes = Boxes(torch.as_tensor([p["bbox"] for p in gt["annotations"]], dtype=float).reshape(-1, 4))
        gt_classes = np.array([p["category_id"] for p in gt["annotations"]], dtype=int)
        pred_boxes = prediction.pred_boxes
        pred_classes = prediction.pred_classes.numpy().astype(int)
        pred_scores = prediction.scores.numpy()
        classes = set(gt_classes.tolist()).union(pred_classes.tolist())
        if ignore_class_label_for_overall_performance:
            classes.add(-1)
        for cls in classes:
            if cls == -1:
                gt_mask_cls = [True] * len(gt_classes)
                pred_mask_cls = [True] * len(pred_classes)
            else:
                gt_mask_cls = gt_classes == cls
                pred_mask_cls = pred_classes == cls
            gt_boxes_cls = Boxes(gt_boxes.tensor[gt_mask_cls])
            pred_boxes_cls = Boxes(pred_boxes.tensor[pred_mask_cls])
            pred_scores_cls = pred_scores[pred_mask_cls]
            if pred_box_overlap_threshold:
                if keep_overlapping_box.lower() == 'biggest':
                    order = np.argsort(pred_boxes_cls.area)
                elif keep_overlapping_box.lower() == 'highest_score':
                    order = np.argsort(pred_scores_cls)
                else:
                    raise ValueError('Implemented options for `keep_overlapping_box` are `biggest` and `highest_score`.')
                pred_boxes_cls.tensor = pred_boxes_cls.tensor[order]
                pred_scores_cls = pred_scores_cls[order]
                iou = pairwise_iou(pred_boxes_cls, pred_boxes_cls)
                keep = np.ones_like(pred_scores_cls, dtype=bool)
                for idx, box in enumerate(pred_boxes_cls):
                    if idx == 0:
                        continue
                    keep[idx] = all(iou[idx, :idx] < pred_box_overlap_threshold)
                pred_boxes_cls = pred_boxes_cls[keep]
                pred_scores_cls = pred_boxes_cls[keep]
            iou = pairwise_iou(gt_boxes_cls, pred_boxes_cls)
            matcher = Matcher([min_iou_for_hit], [0, 1])
            matches, match_labels = matcher(iou)
            match_labels = match_labels.numpy().astype(bool)
            matches = matches.numpy()
            for thresh in thresholds:
                not_ignore = pred_scores_cls >= thresh
                is_match = np.logical_and(not_ignore, match_labels)
                matches_bool = np.zeros(len(gt_boxes_cls), dtype=bool)
                matches_bool[np.unique(matches[is_match])] = True
                tp_i =  np.sum(matches_bool)
                scores[thresh][cls]['tp'] += tp_i
                scores[thresh][cls]['fn'] += len(gt_boxes_cls) - tp_i
                scores[thresh][cls]['fp'] += np.sum(np.logical_and(not_ignore, np.logical_not(match_labels)))

    def get_recall_precision_auc(thresholds, dict_f, sum_dict=None):
        recall = np.zeros(len(thresholds), dtype=float)
        precision = np.zeros(len(thresholds), dtype=float)
        for i, t in enumerate(thresholds):
            tp = dict_f(t)['tp']
            fp = dict_f(t)['fp']
            fn = dict_f(t)['fn']
            recall[i] = tp / (tp + fn) if tp + fn > 0 else 0.
            precision[i] = tp / (tp + fp) if tp + fp > 0 else 0.
            if sum_dict is not None:
                sum_dict[t]['tp'] += tp
                sum_dict[t]['fp'] += fp
                sum_dict[t]['fn'] += fn
        if add_curve_points:
            return {'cls-recall': recall.tolist(),
                    'cls-precision': precision.tolist(),
                    'cls-thresholds': thresholds.tolist(),
                    'mAP': _call_mAP(recall, precision)}
        else:
            return _call_mAP(recall, precision)

    metrics = {}
    all_classes = set([*itertools.chain(*[[*v.keys()] for v in scores.values()])])
    values_all_classes = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
    for cls in all_classes:
        values = get_recall_precision_auc(thresholds, lambda t: scores[t][cls], values_all_classes)
        if cls == -1:
            cls = 'allClasses'
        else:
            cls = str(cls) if class_names is None else class_names[int(cls)]
        metrics[str(cls) if add_curve_points else f'mAP/{cls}'] = values
    if not ignore_class_label_for_overall_performance:
        metrics['allClasses' if add_curve_points else 'mAP/allClasses'] = get_recall_precision_auc(thresholds, lambda t: values_all_classes[t])
    return metrics


def _call_mAP(recall, precision, points=np.arange(0., 1.0+1e-5, 0.1)):
    order = np.argsort(recall)
    recall = recall[order]
    precision = precision[order]
    return np.mean([np.max(precision[recall >= p], initial=0) for p in points])
