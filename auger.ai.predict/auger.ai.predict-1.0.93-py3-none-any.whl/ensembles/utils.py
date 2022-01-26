import copy

import numpy as np
from sklearn.preprocessing import LabelBinarizer

from auger_ml.ensembles.metrics import *
from auger_ml.scores.regression import *

def preds_accumulator(pred, y_pred, preds_cnt=2):
    try:
        y_pred += pred
    except (IndexError, TypeError, ValueError):
        preds_cnt = max(1, preds_cnt - 1)
    return y_pred, preds_cnt


def __export_to_pipeline(algorithm_name, algorithm_params, options):
    from auger_ml.core.AugerML import AugerML

    options = copy.copy(options)
    options['algorithm_name'] = algorithm_name
    options['algorithm_params'] = algorithm_params
    options['ensemble'] = False
    options['trialClass'] = None
    options = AugerML(options).update_task_params(options)
    return AugerML(options).create_model_by_trial(options)


def get_pipelines(predictions, options):
    return [__export_to_pipeline(p['name'], p['params'], options) for p in predictions]


def filter_weights_and_pipelines(weights, predictions):
    new_weigts, new_pipelines = [], []
    for i, w in enumerate(weights):
        if w > 1e-6:
            new_weigts.append(w)
            new_pipelines.append({'name': predictions[i]['name'],
                                  'params': predictions[i]['params'],
                                  'uid': predictions[i]['uid']})
    return new_weigts, new_pipelines


def _accuracy(y, y_probs):
    """return accuracy score"""
    return accuracy_score(y, np.argmax(y_probs, axis=1))


def _average_precision(y, y_probs):
    return average_precision_score(y, np.argmax(y_probs, axis=1))


def _cohen_kappa(y, y_probs):
    return cohen_kappa_score(y, np.argmax(y_probs, axis=1))


def _matthews_corrcoef(y, y_probs):
    return matthews_corrcoef(y, np.argmax(y_probs, axis=1))


def _f1(y, y_probs):
    """return f1 score"""
    return f1_score(y, np.argmax(y_probs, axis=1))


def _f1_micro(y, y_probs):
    return f1_score(y, np.argmax(y_probs, axis=1), average='micro')


def _f1_macro(y, y_probs):
    return f1_score(y, np.argmax(y_probs, axis=1), average='macro')


def _f1_weighted(y, y_probs):
    return f1_score(y, np.argmax(y_probs, axis=1), average='weighted')


def _precision(y, y_probs):
    """return precision score"""
    return precision_score(y, np.argmax(y_probs, axis=1))


def _precision_micro(y, y_probs):
    return precision_score(y, np.argmax(y_probs, axis=1), average='micro')


def _precision_macro(y, y_probs):
    return precision_score(y, np.argmax(y_probs, axis=1), average='macro')


def _precision_weighted(y, y_probs):
    return precision_score(y, np.argmax(y_probs, axis=1), average='weighted')


def _recall(y, y_probs):
    """return recall score"""
    return recall_score(y, np.argmax(y_probs, axis=1))


def _recall_micro(y, y_probs):
    return recall_score(y, np.argmax(y_probs, axis=1), average='micro')


def _recall_macro(y, y_probs):
    return recall_score(y, np.argmax(y_probs, axis=1), average='macro')


def _recall_weighted(y, y_probs):
    return recall_score(y, np.argmax(y_probs, axis=1), average='weighted')


def _auc(y, y_probs):
    """return AUC score (for binary problems only)"""
    return roc_auc_score(y, y_probs[:, 1])


def _neg_log_loss(y, y_probs):
    return -log_loss(y, y_probs)


def _rmse(y_bin, y_probs):
    """return 1-rmse since we're maximizing the score for hillclimbing"""
    return 1.0 - np.sqrt(mean_squared_error(y_bin, y_probs))


def _mxentropy(y_bin, y_probs, eps=1e-7):
    """return negative mean cross entropy since we're maximizing the score for hillclimbing"""
    clipped = np.clip(y_probs, eps, 1.0 - eps)
    clipped /= clipped.sum(axis=1)[:, np.newaxis]

    return (y_bin * np.log(clipped)).sum() / y_bin.shape[0]

# def _neg_rmsle(y_true, y_pred):
#     return -np.sqrt(mean_squared_log_error(y_true, y_pred))

# def _neg_rmse(y_true, y_pred):
#     return -np.sqrt(mean_squared_error(y_true, y_pred))

# def _neg_mase(y_true, y_pred):
#     numerator = np.sum(np.abs(y_true - y_pred))
#     coeff = y_true.shape[0] / (y_true.shape[0] - 1)
#     denominator = np.sum(np.abs(y_true[1:] - y_true[:-1]))
#     return -numerator / (denominator * coeff)

# def _neg_mape(y_true, y_pred):
#     eps = 1e-6
#     result = -np.sum(np.abs((y_true - y_pred) / (y_true + eps))) / len(y_true)

#     return float(result)


# def _mda(y_true, y_pred, epsilon=1e-6):
#     """ https://en.wikipedia.org/wiki/Mean_Directional_Accuracy """
#     n_elements = max(1, y_true[np.abs(y_true) > epsilon].shape[0])
#     true_sign = np.sign(y_true[1:] - y_true[:-1])
#     pred_sign = np.sign(y_pred[1:] - y_pred[:-1])
#     match = (true_sign == pred_sign).sum()
#     return match / float(n_elements)


_scores = {
        'accuracy': _accuracy,
        'average_precision': _average_precision,
        'f1': _f1,
        'f1_micro': _f1_micro,
        'f1_macro': _f1_macro,
        'f1_weighted': _f1_weighted,
        'precision': _precision,
        'precision_micro': _precision_micro,
        'precision_macro': _precision_macro,
        'precision_weighted': _precision_weighted,
        'recall': _recall,
        'recall_micro': _recall_micro,
        'recall_macro': _recall_macro,
        'recall_weighted': _recall_weighted,
        'roc_auc': _auc,
        'neg_log_loss': _neg_log_loss,
        'rmse': _rmse,
        'xentropy': _mxentropy,
        'neg_rmsle': neg_rmsle_score,
        'neg_rmse': neg_rmse_score,
        'neg_mase': neg_mase_score,
        'neg_mape': neg_mape_score,
        'mda': mda_score,
        'cohen_kappa': _cohen_kappa,
        'matthews_corrcoef': _matthews_corrcoef,
    }

_labels = ('_macro', '_micro', '_samples', '_weighted')
_common = ('log_loss', '_score', 'matthews_corrcoef')


def _get_score_func_by_name(score_name):
    score_to_import = score_name
    if not score_name.endswith(_labels+_common):
        score_to_import = score_name + '_score'

    import auger_ml.ensembles.metrics
    func = getattr(auger_ml.ensembles.metrics, score_to_import)

    if score_to_import.endswith(_labels):
        return ScoreWrapper(func, score_to_import)
    return func


class ScoreWrapper(object):
    def __init__(self, func, score_to_import):
        self.func = func
        self.label = score_to_import.split('_')[-1]

    def __call__(self, y_true, y_pred):
        return self.func(y_true, y_pred, average=self.label)


def get_score_func(score_name, classification=False):
    if classification:
        score_name = [k for k in _scores if k == score_name]
        if not score_name:
            return _accuracy, 'accuracy'
        else:
            return _scores[score_name[0]], score_name[0]
    else:   # regression
        if score_name in _scores:
            return _scores[score_name], score_name
        else:
            return _get_score_func_by_name(score_name), score_name


def labels_to_score_transform(score_name, y, n_classes):
    if score_name in ('rmse', 'xentropy'):
        # binarize
        if n_classes > 2:
            return LabelBinarizer().fit_transform(y)
        else:
            return np.column_stack((1 - y, y))
    return y
