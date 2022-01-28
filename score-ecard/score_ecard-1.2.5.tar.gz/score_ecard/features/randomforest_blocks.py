# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 12:23
Desc:
'''

import numpy as np
from collections import OrderedDict

def get_randomforest_blocks(clf_rf, col_name=None, valid_feature_prob=1.0, cross_hierarchy=0):
    '''
    利用随机森林获得最优分箱的边界值列表
    :param clf_rf:
    :param col_name:
    :param valid_feature_prob: 选择随机森林有效特征的比例，剔除低重要度特征，建议在0.85~1.0
    :param cross_hierarchy: 各决策树内进行特征交叉的层深
    :return:
    rf_cross_boundary: 各决策树的前n层特征及boundary，用来特征交叉
    '''
    rf_boundary = []
    rf_cross_boundary = []
    importances = clf_rf.feature_importances_
    indices = np.argsort(importances)[::-1]
    col_set = indices[importances[indices].cumsum() <= valid_feature_prob]
    for i, treei in enumerate(clf_rf.estimators_):
        n_nodes = treei.tree_.node_count
        feature_idx = treei.tree_.feature
        if col_name is not None:
            feature = np.array([(col_name[i] if i>=0 else i)for i in feature_idx])
        else:
            feature = feature_idx
        threshold = treei.tree_.threshold
        children_left = treei.tree_.children_left
        children_right = treei.tree_.children_right
        tree_boundary = {}
        for j in range(n_nodes):
            if feature_idx[j] not in col_set:
                continue
            if children_left[j] != children_right[j]:  # 获得决策树节点上的划分边界值(除叶子结点)
                if feature[j] in tree_boundary:
                    boundary = tree_boundary.get(feature[j])
                    boundary.append(threshold[j])
                else:
                    boundary = [-np.inf, np.inf]
                    boundary.append(threshold[j])
                tree_boundary.update({feature[j]: boundary})
        for k, v in tree_boundary.items():
            sv = list(set([round(i, 4) for i in v]))
            sv.sort()
            tree_boundary.update({k: sv})
        rf_boundary.append(tree_boundary)

        # extend cross feature
        ext_features = OrderedDict()
        if cross_hierarchy >= 2:
            step_n = cross_hierarchy
            cross_feature = {feature[0]: [-np.inf, threshold[0], np.inf]}
            cur_list = [0]
            while (step_n > 1):
                next_list = []
                for cur_ in cur_list:
                    left_ = children_left[cur_]
                    right_ = children_right[cur_]
                    for i in [left_, right_]:
                        if i < 0:
                            continue
                        cur_feature = feature[i]
                        cur_threshold = threshold[i]
                        if cur_feature in cross_feature:
                            boundary_ = cross_feature.get(cur_feature)
                            boundary_.append(cur_threshold)
                        else:
                            boundary_ = [-np.inf, cur_threshold, np.inf]
                        cross_feature.update({cur_feature: boundary_})
                        next_list.append(i)
                cur_list = next_list
                step_n -= 1
            col_sorted = col_name[indices] if col_name is not None else indices
            for icol in col_sorted:
                v = cross_feature.get(icol)
                if v:
                    sv = list(set([round(i, 4) for i in v]))
                    sv.sort()
                    ext_features.update({icol: sv})
        rf_cross_boundary.append(ext_features)
    return rf_boundary, rf_cross_boundary



