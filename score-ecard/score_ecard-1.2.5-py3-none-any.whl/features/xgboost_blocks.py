# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 12:23
Desc:
'''

import numpy as np

def get_xgboost_blocks(clf_xgb, col_name=None, valid_feature_prob=1.0):
    '''
    利用xgb获得最优分箱的边界值列表
    :param clf_xgb:
    :param col_name:
    :param valid_feature_prob: 选择随机森林有效特征的比例，剔除低重要度特征，建议在0.85~1.0
    :return:
    '''
    importances = clf_xgb.feature_importances_
    indices = np.argsort(importances)[::-1]
    col_set = col_name[importances[indices].cumsum() <= valid_feature_prob]
    booster = clf_xgb.get_booster()
    df_trees = booster.trees_to_dataframe()
    df_trees = df_trees[df_trees.Feature.isin(col_set)]
    df_boundary = df_trees.groupby(['Tree', 'Feature'])['Split'].apply(
        lambda x: sorted([-np.inf,np.inf]+list(set(x)))).unstack().applymap(
        lambda x: [-np.inf,np.inf] if (x==None) or str(x)=='nan' else x)
    xgb_boundary = [dict(j) for i, j in df_boundary.iterrows()]
    return xgb_boundary
