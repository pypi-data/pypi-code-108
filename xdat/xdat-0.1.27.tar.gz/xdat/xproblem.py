import numpy as np
import pandas as pd
from collections import namedtuple
from sklearn import model_selection, pipeline, metrics
from sklearn.base import clone
from . import xutils


Metric = namedtuple('Metric', ['name', 'func', 'args'])
METRICS = {
    'auc': Metric(name='auc', func=metrics.roc_auc_score, args=['target', 'prob_1'])
}


def cv_split(df, n_splits=12, stratify_on=None, group_on=None):
    df = df.sample(frac=1.).reset_index(drop=True)
    groups = df[group_on] if group_on else None
    y = df[stratify_on] if stratify_on else None

    if group_on is None:
        if n_splits == 'max':
            n_splits = len(df)

        if stratify_on:
            kfold = model_selection.StratifiedKFold(n_splits=n_splits)

        else:
            kfold = model_selection.KFold(n_splits=n_splits)

    else:
        num_groups = len(np.unique(groups))
        if n_splits == 'max':
            n_splits = num_groups

        n_splits = min(n_splits, num_groups)

        if stratify_on:
            kfold = model_selection.StratifiedGroupKFold(n_splits=n_splits)

        else:
            kfold = model_selection.GroupKFold(n_splits=n_splits)

    for train_index, test_index in kfold.split(df, y=y, groups=groups):
        df_train = df.iloc[train_index].reset_index(drop=True)
        df_test = df.iloc[test_index].reset_index(drop=True)
        yield df_train, df_test


CVFold = namedtuple("CVFold", ['clf', 'df_train', 'df_test', 'feature_names'])


def train_cv(df, target_col, clf, n_splits=12, stratify_on=None, group_on=None, ordered_split=False, del_cols=tuple(), uid_col=None, sample_weight_col=None):
    del_cols = set(del_cols)
    if uid_col:
        del_cols.add(uid_col)
    if sample_weight_col:
        del_cols.add(sample_weight_col)
    del_cols = sorted(del_cols)

    all_folds = []
    fold_num = 1

    for df_train, df_test in cv_split(df, n_splits=n_splits, stratify_on=stratify_on, group_on=group_on):
        clf_fold = clone(clf)
        df_test_data = df_test.copy()
        test_tmp_uid = df_test[uid_col] if uid_col else None
        sample_weight = df_train[sample_weight_col] if sample_weight_col else None

        if ordered_split and group_on:
            assert n_splits == 'max'
            test_group = df_test[group_on].min()
            df_train = df_train[df_train[group_on] < test_group].reset_index(drop=True)
            assert (df_train[group_on] >= test_group).sum() == 0
            if len(df_train) == 0:
                continue

        if del_cols:
            df_train.drop(columns=del_cols, errors='ignore', inplace=True)
            df_test_data = df_test.drop(columns=del_cols, errors='ignore')

        # offs = df_train.groupby('p').mean()[['target']].reset_index()
        # offs.columns = ['p', 'offset']
        # print(offs)
        # df_test = df_test.merge(offs, how = 'left', on=['p'])
        # df_test['offset'] = df_test['offset'].fillna(df_train['target'].mean())
        X_train, y_train = xutils.split_X_y(df_train, target_col)

        if sample_weight is not None:
            clf_fold.fit(X_train, y_train, sample_weight=sample_weight)

        else:
            clf_fold.fit(X_train, y_train)

        #print(clf_fold[2].coef_)
        X_test, y_test = xutils.split_X_y(df_test_data, target_col)
        pred = clf_fold.predict(X_test)
        df_test['pred'] = pred

        if hasattr(clf_fold, "predict_proba"):
            prob_1 = clf_fold.predict_proba(X_test)[:, 1]
            df_test['prob_1'] = prob_1

        df_test['fold_num'] = fold_num
        if uid_col:
            df_test[uid_col] = test_tmp_uid

        fold = CVFold(clf=clf_fold, df_train=df_train, df_test=df_test, feature_names=X_train.columns)
        all_folds.append(fold)
        fold_num += 1

    df_test = pd.concat([i[2] for i in all_folds], ignore_index=True)
    df_test = df_test.reset_index(drop=True)
    return df_test, all_folds


def eval_test(df_test, eval_per=None, metric_list=None):
    """

    :type metrics: list[Metric|str]
    """

    df_test = df_test.copy()
    df_test['none'] = 'none'

    metric_list = [m if isinstance(m, Metric) else METRICS[m] for m in metric_list]

    if not isinstance(eval_per, list) and not isinstance(eval_per, tuple):
        eval_per = [eval_per]

    rows = []
    for curr_group in eval_per:
        if not curr_group:
            curr_group = 'none'

        for gval in df_test[curr_group].unique():
            df_g = df_test[df_test[curr_group] == gval]
            row = {m.name: m.func(*(df_g[arg] for arg in m.args)) for m in metric_list}
            row['cv_grouping'] = curr_group
            row['cv_group_key'] = str(gval)
            row['cv_group_size'] = len(df_g)
            rows.append(row)

    df_res = pd.DataFrame(rows)
    return df_res


def calc_feature_importances(folds, flat=False):
    rows = []
    fi_var = None
    for fold in folds:
        clf = fold.clf
        if isinstance(clf, pipeline.Pipeline):
            clf = clf[-1]

        if fi_var is None:
            for var in ['feature_importances_', 'coef_']:
                if hasattr(clf, var):
                    fi_var = var
                    break

            if not fi_var:
                print("Can't find in clf")
                return

        fi = getattr(clf, fi_var).flatten()
        fi_dict = dict(zip(fold.feature_names, fi))
        if flat:
            for k, v in fi_dict.items():
                rows.append({'feature_name': k, 'feature_importance': v})

        else:
            rows.append(fi_dict)

    df = pd.DataFrame(rows)
    return df
