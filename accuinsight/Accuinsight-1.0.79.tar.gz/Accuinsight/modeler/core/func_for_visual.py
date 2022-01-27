from collections import OrderedDict
import numpy as np
from scipy import interpolate


def delete_nan(lst):
    if np.isnan(lst).any():
        idx = np.where(np.isnan(lst))[0].tolist()

        for i in idx:
            lst.pop(i)
    
    return lst


def sort(x):
    sort_result = np.sort(x)[::-1]
    sort_idx = x.argsort()[::-1]
    return {'x': sort_result, 'idx':sort_idx}


def moving_average(a, n) :
    cumsum = np.cumsum(a, dtype=float)
    cumsum[n:] = cumsum[n:] - cumsum[:-n]
    return cumsum[n - 1:] / n


def cal_confusion(y_test_vec, y_score_vec, force_diag = True):
    results = OrderedDict()
    y_score_vec_sort = sort(y_score_vec)
    y_score_vec = y_score_vec_sort['x']
    y_test_vec = y_test_vec[y_score_vec_sort['idx']]
    
    results['TP'] = np.cumsum(y_test_vec==1)
    results['FP'] = np.cumsum(y_test_vec==0)
    results['FN'] = np.sum(y_test_vec==1) - results['TP']
    results['TN'] = np.sum(y_test_vec==0) - results['FP']
    
    results['TPR'] = results['TP']/(results['TP'] + results['FN'])
    results['FPR'] = results['FP']/(results['FP'] + results['TN'])
    results['PPV'] = results['TP']/(results['TP'] + results['FP'])
    
    if force_diag:
        results['TPR'] = np.r_[np.array(0), results['TPR']]
        results['FPR'] = np.r_[np.array(0), results['FPR']]
        results['PPV'] = np.r_[results['PPV'][0], results['PPV']]
    return results


def cal_auc(tpr, ppv):
    idx = tpr.argsort(kind='stable')
    return np.sum(np.diff(tpr[idx]) * moving_average(ppv[idx], 2))


def multi_pr(y_test, y_score):
    recall = OrderedDict()
    precision = OrderedDict()
    auc = OrderedDict()

    class_names = np.array(range(y_test.shape[0]))
    # press data
    press_num = 1000

    for i in range(len(class_names)):
        y_test_vec = np.array(y_test[i])
        y_score_vec = np.array(y_score[i])
    
        if len(y_test_vec) >= 2000:
            p = int(np.around(len(y_test_vec)/press_num))
        else:
            p = 1

        confus = cal_confusion(y_test_vec, y_score_vec, force_diag = True)
        recall[i] = confus['TPR'][::p].tolist()
        precision[i] = confus['PPV'][::p].tolist()
        auc[i] = cal_auc(confus['TPR'][::p], confus['PPV'][::p])
    
    all_recall = np.sort(np.unique(np.array([recall[i] for i in range(len(recall))]).flatten()))[::-1]
    all_precision = np.zeros_like(all_recall)

    for i in range(len(class_names)):
        f = interpolate.interp1d(recall[i], precision[i], kind='linear', fill_value="extrapolate")
        all_precision = all_precision + f(all_recall)

    all_precision = all_precision/len(class_names)

    if len(all_recall) >= 2000:
            p = int(np.around(len(all_recall)/press_num))
    else:
            p = 1

    recall['macro'] = all_recall[::p].tolist()
    precision['macro'] = all_precision[::p].tolist()
    auc['macro'] = cal_auc(all_recall[::p], all_precision[::p])

    y_test_vec_bin = y_test.flatten()
    y_score_vec_bin = y_score.flatten()
    confus_bin = cal_confusion(y_test_vec_bin, y_score_vec_bin)

    if len(y_test_vec_bin) >= 2000:
        p = int(np.around(len(y_test_vec_bin)/press_num))
    else:
        p = 1

    recall['micro'] = confus_bin['TPR'][::p].tolist()
    precision['micro'] = confus_bin['PPV'][::p].tolist()
    auc['micro'] = cal_auc(confus_bin['TPR'][::p], confus_bin['PPV'][::p])
    
    
    # nan 값이 나오더라도 json 저장 가능하도록
    delete_nan(recall['macro'])
    delete_nan(precision['macro'])
    delete_nan(recall['micro'])
    delete_nan(precision['micro'])
    
    if str(auc['macro']) == 'nan':
        auc['macro'] = int(0)
    if str(auc['micro']) == 'nan':
        auc['micro'] = int(0)
    
    
    res_dict = OrderedDict()
    if len(class_names) <= 5:
        res_dict['recall'] = recall
        res_dict['precision'] = precision
        res_dict['auc'] = auc
    else:
        res_dict['recall'] = {'macro': recall['macro']}
        res_dict['recall']['micro'] = recall['micro']
        res_dict['precision'] = {'macro': precision['macro']}
        res_dict['precision']['micro'] = precision['micro']
        res_dict['auc'] = {'macro': auc['macro']}
        res_dict['auc']['micro'] = auc['micro']
    
    return(res_dict)

def multi_roc(y_test, y_score):
    fpr = OrderedDict()
    tpr = OrderedDict()
    auc = OrderedDict()

    class_names = np.array(range(y_test.shape[0]))

    # press data
    press_num = 1000

    for i in range(len(class_names)):
        y_test_vec = np.array(y_test[i])
        y_score_vec = np.array(y_score[i])
    
        if len(y_test_vec) >= 2000:
            p = int(np.around(len(y_test_vec)/press_num))
        else:
            p = 1

        confus = cal_confusion(y_test_vec, y_score_vec, force_diag=True)
        fpr[i] = confus['FPR'][::p].tolist()
        tpr[i] = confus['TPR'][::p].tolist()
        auc[i] = cal_auc(1-confus['FPR'][::p], confus['TPR'][::p])
    
    all_fpr = np.sort(np.unique(np.array([fpr[i] for i in range(len(fpr))]).flatten()))[::-1]
    all_tpr = np.zeros_like(all_fpr)

    for i in range(len(class_names)):
        f = interpolate.interp1d(fpr[i], tpr[i], kind='linear', fill_value='extrapolate')
        all_tpr = all_tpr + f(all_fpr)

    all_tpr = all_tpr/len(class_names)

    if len(all_fpr) >= 2000:
            p = int(np.around(len(all_fpr)/press_num))
    else:
            p = 1

    fpr['macro'] = all_fpr[::p].tolist()
    tpr['macro'] = all_tpr[::p].tolist()
    auc['macro'] = cal_auc(all_fpr[::p], all_tpr[::p])

    y_test_vec_bin = y_test.flatten()
    y_score_vec_bin = y_score.flatten()
    confus_bin = cal_confusion(y_test_vec_bin, y_score_vec_bin)

    if len(y_test_vec_bin) >= 2000:
        p = int(np.around(len(y_test_vec_bin)/press_num))
    else:
        p = 1

    fpr['micro'] = confus_bin['FPR'][::p].tolist()
    tpr['micro'] = confus_bin['TPR'][::p].tolist()
    auc['micro'] = cal_auc(confus_bin['FPR'][::p], confus_bin['TPR'][::p])
    
    # nan 값이 나오더라도 json 저장 가능하도록
    delete_nan(fpr['macro'])
    delete_nan(tpr['macro'])
    delete_nan(fpr['micro'])
    delete_nan(tpr['micro'])
    
    if str(auc['macro']) == 'nan':
        auc['macro'] = int(0)
    if str(auc['micro']) == 'nan':
        auc['micro'] = int(0)
    
    res_dict = OrderedDict()
    if len(class_names) <= 5:
        res_dict['fpr'] = fpr
        res_dict['tpr'] = tpr
        res_dict['auc'] = auc
    else:
        res_dict['fpr'] = {'macro': fpr['macro']}
        res_dict['fpr']['micro'] = fpr['micro']
        res_dict['tpr'] = {'macro': tpr['macro']}
        res_dict['tpr']['micro'] = tpr['micro']
        res_dict['auc'] = {'macro': auc['macro']}
        res_dict['auc']['micro'] = auc['micro']
    
    return(res_dict)

