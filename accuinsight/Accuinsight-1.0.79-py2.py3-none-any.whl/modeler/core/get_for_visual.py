import warnings
from collections import OrderedDict
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from Accuinsight.modeler.core import get
from Accuinsight.modeler.core.func_for_visual import cal_confusion, cal_auc, multi_roc, multi_pr


def y_test_reshape(y_test):
    # dataframe/series형 np.array로 형 변환
    if 'pandas' in str(type(y_test)):
        y_test = np.array(y_test)
        
    try:
        n_classes = len(np.unique(y_test, axis = 0))
    except:
        n_classes = len(np.unique(y_test))

    if y_test.ndim == 1:
        y_test = y_test
    elif y_test.ndim == 2:
        if y_test.shape[1] == n_classes:
            y_test = np.array([np.where(y_test[i]==np.max(y_test[i]))[0].tolist() for i in range(len(y_test))]).flatten()
        else:
            y_test = y_test.flatten()
    return y_test


def y_test_to_categorical(y_test):
    try:
        n_classes = len(np.unique(y_test, axis=0))
    except:
        n_classes = len(np.unique(y_test))
        
    enc = OneHotEncoder(categories = 'auto')

    if y_test.ndim == 1:
        if 'Series' in str(type(y_test)):
            y_test = np.array(y_test)
        elif type(y_test) == list:
            y_test = np.array(y_test)
            
        y_test2d = y_test.reshape(-1,1)
        y_test_cat = enc.fit_transform(y_test2d).toarray()
    
    elif y_test.ndim == 2 and y_test.shape[1] == n_classes:  # y_test: categorical
        y_test_cat = y_test

    return y_test_cat


def y_pred_reshape(model, X_test):
    prob = model.predict(X_test)

    if prob.ndim == 1:
        y_pred = [1 if i >= 0.5 else 0 for i in prob]

    elif prob.ndim == 2:
        if prob.shape[1] == 1:
            y_prob = np.c_[1-prob, prob]
            y_pred = np.array([np.where(y_prob[i] == np.max(y_prob[i]))[0].tolist() for i in range(len(y_prob))]).flatten()
        else:
            y_prob = prob
            y_pred = np.array([np.where(y_prob[i]==np.max(y_prob[i]))[0].tolist() for i in range(len(y_prob))]).flatten()
    return y_pred


def y_pred_to_categorical(model, X_test, y_test):
    try:
        n_classes = len(np.unique(y_test, axis = 0))
    except:
        n_classes = len(np.unique(y_test))
        
    prob = model.predict(X_test)
    enc = OneHotEncoder(categories = 'auto')
    y_pred_cat = None

    if prob.ndim == 1:
        prob = np.array([1 if i>=0.5 else 0 for i in prob])
        y_pred2d = prob.reshape(-1,1)
        y_pred_cat = enc.fit_transform(y_pred2d).toarray()

    elif prob.ndim == 2:
        if n_classes == 2 and prob.shape[1] == n_classes-1:
            prob = np.c_[1-prob, prob]
            y_pred_cat = np.zeros_like(prob)
            for i in range(y_pred_cat.shape[0]):
                y_pred_cat[i][np.where(prob[i] == np.max(prob[i]))[0]] = 1
    
        elif prob.shape[1] == n_classes:  # y_test: categorical
            y_pred_cat = np.zeros_like(prob)
            for i in range(y_pred_cat.shape[0]):
                y_pred_cat[i][np.where(prob[i] == np.max(prob[i]))[0]] = 1

    return y_pred_cat


def y_score_proba(model, X_test, y_test):
    y_score = None
    if get.model_type(model) == 'SVC' and 'probability=False' in str(model):
        if len(model.classes_) == 2:
            d = model.decision_function(X_test)
            prob = (d - d.min()) / (d.max() - d.min())
            y_score = np.c_[prob, 1-prob]
        else:
            warnings.warn('"probability = True" 설정이 필요합니다.')

    elif get.model_type(model) == 'LinearSVC':
        if len(model.classes_) == 2:
            d = model.decision_function(X_test)
            prob = (d - d.min()) / (d.max() - d.min())
            y_score = np.c_[prob, 1-prob]
        else:
            warnings.warn('label의 갯수가 3 이상인 경우, LinearSVC에서 "predict_proba"를 제공하지 않아 metric 계산이 불가능합니다. 자세한 사항은 사용자 매뉴얼을 참조하십시오.')
            
    elif 'keras' in get.model_type(model):
#       prob = model.predict_proba(X_test)   -- predict_proba() is deprecated.
        prob = model.predict(X_test)
        if len(np.unique(y_test, axis = 0)) == 2 and prob.shape[1] == 1:
            y_score = np.c_[1-prob, prob]
            
        else:
            y_score = prob
    
    else:
        if hasattr(model, 'predict_proba'):
            y_score = model.predict_proba(X_test)
        else:
            y_score = model.predict(X_test)
            if y_score.ndim == 1:
                y_score = np.c_[y_score, 1-y_score]
    return y_score


# (DL & ML) & Classification
def roc_pr_curve(model, X_test, y_test, *args):
    # y_test (dim=2/dim=1, 두 가지 경우 존재)
    # y_test는 categorical var. 변경 필요
    y_test = y_test_reshape(y_test)
    y_test_cat = y_test_to_categorical(y_test)

    # y_score (SVC 사용한 경우, decision_function으로 계산)
    y_score = y_score_proba(model, X_test, y_test)

    # y_pred (dim=2/dim=1, 두 가지 경우 존재)
    y_pred = y_pred_reshape(model, X_test)

    # list of labels
    if hasattr(model, 'classes_'):   # case 1: ML
        if 'float' in str(model.classes_.dtype) or 'int' in str(model.classes_.dtype):
            label_list = np.unique(model.classes_).astype('int').tolist()
        else:
            label_list = np.unique(model.classes_).tolist()
    else:   # case 2: DL
        classes_dl = np.unique(y_test, axis=0)
        if 'float' in str(classes_dl.dtype) or 'int' in str(classes_dl.dtype):
            label_list = classes_dl.astype('int').tolist()
        else:
            label_list = classes_dl.tolist()

    # results
    res_dict = OrderedDict()
    
    if y_score is not None:
        res_roc = multi_roc(y_test_cat.T, y_score.T)
        res_pr = multi_pr(y_test_cat.T, y_score.T)
    else:
        res_dict['ValueError'] = True

    res_dict['fpr'] = res_roc['fpr']
    res_dict['tpr'] = res_roc['tpr']
    res_dict['recall'] = res_pr['recall']
    res_dict['precision'] = res_pr['precision']

    res_dict['legend'] = {'roc': res_roc['auc'], 'precision-recall': res_pr['auc']}
    res_dict['confusion_matrix'] = dict(zip(label_list, confusion_matrix(y_test, y_pred, labels=label_list).tolist()))
    res_dict['chart'] = {'AUC': res_roc['auc']['micro'],
                         'Precision': res_pr['auc']['micro'],
                         'Recall': recall_score(y_test, y_pred, average='micro'),
                         'F1-score': f1_score(y_test, y_pred, average='micro')}
    return res_dict


# (DL & ML) & Regression
def get_true_y(y_test):
    # reshape (dim2 -> dim1)
    if len(y_test.shape) == 2:
        true_y = y_test.reshape(1, -1)[0].tolist()
    elif type(y_test) == list:
        true_y = y_test
    else:
        true_y = y_test.tolist()
    return true_y


def get_visual_info_regressor(model, X_test):
    preds = model.predict(X_test)

    # reshape (dim2 -> dim1)
    if len(preds.shape) == 2:
        preds = preds.reshape(1,-1)[0]

    # 소수점 자리수 조정(소수점 이하 5번째 자리에서 반올림)
    try:
        if len(str(preds[0]).split('.')[1]) >= 5:
            preds = np.round(preds, 4)
            preds = list(map(float, np.array(preds, dtype=str).tolist()))
        else:
            preds = list(map(float, np.array(preds, dtype=str).tolist()))
    except TypeError:
        pass
    return preds
