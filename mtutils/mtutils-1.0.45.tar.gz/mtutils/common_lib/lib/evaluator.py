#
# Class for evaluation (classification/detection/segmentation)
#
from os import isatty
from .data_manager import DataManager
from .anno_manager import AnnotationManager
from .utils import ClassifierEvalMultilabel
from .utils import get_TFPN
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix as compute_confusion_matrix

class EvaluatorBase(object):
    def __init__(self, classname_list=None, data_gt=None, data_pred=None):
        """
        :classname_list: list of classes that we are interested in
        """
        self._classname_list = classname_list
        self._data_gt = data_gt
        self._data_pred = data_pred
        # self.am = None

    def _load_data(self, data):
        if isinstance(data, str):
            return DataManager.load(data)
        elif isinstance(data, DataManager):
            return data
        else:
            raise RuntimeError("Unknown data format: {}".format(type(data)))

    def load_gt(self, data):
        self._data_gt = self._load_data(data)

    def load_pred(self, data):
        self._data_pred = self._load_data(data)

    def set_classnames(self, classname_list):
        if isinstance(classname_list, (tuple, list)):
            self._classname_list = classname_list
        elif isinstance(classname_list, str):
            self._classname_list = [classname_list]
        else:
            raise RuntimeError("Unknown data format: {}".format(type(classname_list)))

    def _check_data(self):
        assert self._data_gt and self._data_pred, "Please load both gt and pred before evaluation."
        assert self._data_gt == self._data_pred, "Make sure the gt data and pred data match"


    # aliases
    load_anno = load_gt
    load_annotation = load_gt
    load_groundtruth = load_gt
    load_prediction = load_pred
    set_class = set_classnames
    set_classname = set_classnames
    set_classname_list = set_classnames




class ClassificationMultiLabelEvaluator(EvaluatorBase):
    def compute_wmAP(self, df, am):
        """ Compute mAP weighted by the actual number ground truth class """
        class_occurrence = self._data_gt.occurrence(lambda rec: am.get_classname(rec))
        class_weights = {key:val / sum(class_occurrence.values()) for key, val in class_occurrence.items()}
        wmAP = sum([class_weights[row.name] * row.AP for _, row in df.iterrows()])
        return wmAP

    def get_am(self):
        if not hasattr(self, 'am'):
            self.am = AnnotationManager(self._data_gt.class_dict)
            classnames = self.am._all_classes if not self._classname_list else self._classname_list
            self.am.setup_distribution_type(distribution_type='multilabel', distribution_classes=classnames)
        return self.am

    def get_distribution_list(self):
        self.get_am()
        self._check_data()

        # collect data for ap computation
        annotation_distribution_list = list()
        prediction_distribution_list = list()
        for rec_anno, rec_pred in self._data_gt.zip(self._data_pred):
            dist_anno = self.am.get_distribution(rec_anno)
            dist_pred = self.am.get_distribution(rec_pred)
            annotation_distribution_list.append(dist_anno)
            prediction_distribution_list.append(dist_pred)
            
        return annotation_distribution_list, prediction_distribution_list

    def eval_miss_fa(self, threshold, class_list=None):
        annotation_distribution_list, prediction_distribution_list = self.get_distribution_list()
        classnames = self.am.classnames
        if class_list is None:
            class_list = self.am.classnames

        for class_name in class_list:
            assert class_name in classnames, f"classname {class_name} not in classnames {classnames}."
        index_list = self.am.get_classid(class_list)

        interested_ann_array = np.array(annotation_distribution_list)[:, index_list]
        interested_pred_array = (np.array(prediction_distribution_list)[:, index_list] > threshold).astype('float64')
        
        class_results = dict()
        
        for index in range(len(class_list)):
            ann_array = interested_ann_array[:, index]
            pred_array = interested_pred_array[:, index]
            info_dict = get_TFPN(ann_array, pred_array)

            class_results[class_list[index]] = info_dict
        return class_results


    def eval_ap(self, verbose=True):
        annotation_distribution_list, prediction_distribution_list = self.get_distribution_list()

        # compute ap
        ap_dict = ClassifierEvalMultilabel.compute_ap(
            y_true  = np.array(annotation_distribution_list),
            y_score = np.array(prediction_distribution_list),
            class_name_list = self.am.classnames
        )
        inflection_info = ClassifierEvalMultilabel.get_inflection_info(
            y_true  = np.array(annotation_distribution_list),
            y_score = np.array(prediction_distribution_list),
            class_name_list = self.am.classnames
        )
        p_at_r_99 = ClassifierEvalMultilabel.compute_p_at_r(            
            y_true  = np.array(annotation_distribution_list),
            y_score = np.array(prediction_distribution_list),
            class_name_list = self.am.classnames,
            recall_thresh=0.99
        )
        thr_at_p_99 = ClassifierEvalMultilabel.get_threshold_at_p(            
            y_true  = np.array(annotation_distribution_list),
            y_score = np.array(prediction_distribution_list),
            class_name_list = self.am.classnames,
            precision_thresh=0.99
        )

        # print evaluation
        if verbose:
            df = pd.DataFrame.from_dict(ap_dict, orient='index', columns=['AP'])
            df_notnull = df[df['AP'].notnull()]  # remove NaN data (No samples of this class in gt)
            print(df_notnull)

            if len(df_notnull) > 1:
                # ap info
                mAP = df_notnull.mean()['AP']
                wmAP = self.compute_wmAP(df_notnull, self.am)
                print('---------------')
                print('AP info')
                print(' mAP: {:.3f}'.format(mAP))
                print('wmAP: {:.3f}\n'.format(wmAP))

                # inflection info
                print()
                print('---------------')
                print('inflection info')
                df_inflection = pd.DataFrame.from_dict(inflection_info).T
                print(df_inflection)
                
                # p_at_r_99
                print()
                print('---------------')
                print('precision at recall 0.99')
                p_at_r_99_pd = pd.DataFrame.from_dict(p_at_r_99, orient='index', columns=['precision_at_recall_0.99'])
                print(p_at_r_99_pd)
                
                # threshold at precision 0.99
                print()
                print('---------------')
                print('threshold at precision 0.99')
                thr_at_p_99_pd = pd.DataFrame.from_dict(thr_at_p_99, orient='index', columns=['threshold_at_precision_0.99'])
                print(thr_at_p_99_pd)

        return ap_dict

    eval = eval_ap
    evaluate = eval_ap
    evaluation = eval_ap


ClassificationEvaluator = ClassificationMultiLabelEvaluator
MultiLabelEvaluator = ClassificationMultiLabelEvaluator


class ClassificationMultiClassEvaluator(EvaluatorBase):
    def eval(self, verbose=True):
        self._check_data()

        am = AnnotationManager(self._data_gt.class_dict)
        classnames = am._leaf_classes if not self._classname_list else self._classname_list
        am.setup_distribution_type(distribution_type='multiclass', distribution_classes=classnames)
        classnames = am.classnames

        # collect data for ap computation
        y_true = list()
        y_pred = list()
        for rec_anno, rec_pred in self._data_gt.zip(self._data_pred):
            classname_anno = am.get_classname(rec_anno)[0]
            classname_pred = am.get_classname(rec_pred)[0]
            y_true.append(classname_anno)
            y_pred.append(classname_pred)

        confusion_mat = compute_confusion_matrix(y_true=y_true, y_pred=y_pred, labels=classnames)
        accuracy = np.mean(np.array(y_true) == np.array(y_pred))

        # compute ap
        ap_dict = {
            'confusion_matrix': confusion_mat,
            'accuracy': accuracy
        }

        # print evaluation
        if verbose:
            df = pd.DataFrame(confusion_mat, index=classnames, columns=classnames)
            df = df.replace(0,'-')
            print()
            print('x-axis: prediction')
            print('y-axis: annotation')
            print(df)
            print("\nAccuracy: {:3f}\n".format(100*accuracy))


        return ap_dict

    evaluate = eval
    evaluation = eval


MultiClassEvaluator = ClassificationMultiClassEvaluator



from .utils import eval_map
class DetectionEvaluator(EvaluatorBase):
    def eval_ap(self, iou_threshold = .1, verbose=True):
        """
        :iou_threshold: the minimal iou that a TP prediction is required when overlapped with a gt bbox
        """
        self._check_data()

        am = AnnotationManager(self._data_gt.class_dict)
        classnames = am._leaf_classes if not self._classname_list else self._classname_list
        am.setup_distribution_type(distribution_type='detection', distribution_classes=classnames)
        classnames = am.classnames

        # collect data for ap computation
        detections = list()
        annotations = list()
        for rec_anno, rec_pred in self._data_gt.zip(self._data_pred):
            # collect detection results
            bboxes = np.reshape(am.get_xyxy(rec_pred),  [-1,4])
            scores = np.reshape(am.get_score(rec_pred), [-1,1])
            labels = np.reshape(am.get_classid(rec_pred), [-1])
            det = np.hstack([bboxes, scores])
            det_res = [det[labels==classid,:] for classid in range(len(am.classnames))]
            detections.append(det_res)

            # collect annotation results
            ann = dict(
                bboxes = np.reshape(am.get_xyxy(rec_anno), [-1,4]),
                labels = np.reshape(am.get_classid(rec_anno), [-1])
            )
            annotations.append(ann)

        # compute ap
        _, ap_results = eval_map(
            det_results=detections,
            annotations=annotations,
            iou_thr=iou_threshold,
        )

        # print evaluation
        if verbose:
            ap_dict = {classname:x['ap'] for classname, x in zip(classnames, ap_results)}
            df = pd.DataFrame.from_dict(ap_dict, orient='index', columns=['AP'])
            df_notnull = df[df['AP'].notnull()]  # remove NaN data (No samples of this class in gt)
            print(df_notnull)

        return ap_results


    eval = eval_ap
    evaluate = eval_ap
    evaluation = eval_ap
