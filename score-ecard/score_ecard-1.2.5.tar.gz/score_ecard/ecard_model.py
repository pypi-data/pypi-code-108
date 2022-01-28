# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 21:51
Desc:
'''
import numpy as np
import pandas as pd
import random
import itertools
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from multiprocessing import Process, Manager

from score_ecard import score_card
from score_ecard.features import layered_woe as woe
from score_ecard.features import randomforest_blocks as rf_bolcks
from score_ecard.features import xgboost_blocks as xgb_bolcks
from score_ecard.util import progress_bar, get_weighted_std, log_run_time, log_cur_time, log_step


class ECardModel():
    def __init__(self,kwargs_lr=None, features_model='rf', kwargs_rf=None, kwargs_xgb=None, sample_frac=1.0,
                 cross_hierarchy=0, is_best_bagging=False, optimize_type='global', n_estimators=None):
        '''

        :param kwargs_lr:
        :param features_model:
        :param kwargs_rf:
        :param kwargs_xgb:
        :param sample_frac: 样本再抽样比例，样本抽样比例 = 0.6*sample_frac
        :param cross_hierarchy: 特征交叉层级，可参考参数设置为[2，3]，默认不进行特征扩展即cross_hierarchy=0
        :param is_best_bagging:
        :param optimize_type: 优化方式={'local': 局部最优, 'global': 全局最优}
        '''
        self.params_lr = {
            "class_weight": 'balanced',
            "penalty": 'l1',
            "C": 0.2,
            "solver": 'liblinear'
        }
        self.params_rf = {
            'n_estimators': 100,
            'max_depth': 5,
            'max_features': 'auto',
            'min_samples_leaf': 0.01,
            'bootstrap': True,
            'class_weight': "balanced",
            'random_state': 666
        }
        self.params_xgb = {
            'n_estimators': 10,
            'max_depth':5,
            'eta': 0.3,
            'min_child_weight': 1,
            'gamma': 0.3,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'booster': 'gbtree',
            'objective': 'binary:logistic',
            'scale_pos_weight': 1,
            'lambda': 1,
            'seed':666,
            'silent': 0,
            'eval_metric': 'auc'
        }
        self.params_base_tree = {
            'max_depth': 10,
            'max_features': None,
            'min_samples_leaf': 0.01,
            'class_weight': "balanced",
            'random_state': 666
        }
        if kwargs_lr:
            self.params_lr.update(**kwargs_lr)
        if kwargs_rf:
            self.params_rf.update(**kwargs_rf)
        if kwargs_xgb:
            self.params_xgb.update(**kwargs_xgb)
        self.features_model = features_model
        self.sample_frac = sample_frac
        self.cross_hierarchy = cross_hierarchy
        self.is_best_bagging = is_best_bagging
        self.optimize_type = optimize_type
        self.init_cards = []
        self.score_ecard = None
        self.cur_card_index = 0
        self.feature_ext_info = {}
        self.score_model = score_card.ScoreCardModel()
        random.seed(666)
        if n_estimators is None:
            self.n_estimators = self.params_rf.get(n_estimators,
                                                   100) if features_model == 'rf' else self.params_xgb.get(n_estimators,
                                                                                                           100)
        else:
            self.n_estimators = n_estimators

    def fit(self, df_X, df_Y, validation_X:pd.DataFrame=None, validation_Y:pd.DataFrame=None, sample_weight=None, validation_step=1):
        self.init_check()
        assert df_X.shape[0] == df_Y.shape[0]
        df_Y, df_y, df_y_binary= self.check_label(df_Y)
        if type(sample_weight)==type(None):
            sample_weight=df_y*0+1

        log_step("start model fitting ...")
        df_X = self.calc_base_card(df_X, df_Y, df_y, df_y_binary, sample_weight)
        ml_boundaries = self.get_ml_boundaries(df_X, df_y, sample_weight=sample_weight)
        random.shuffle(ml_boundaries)
        init_card, df_X_bins = self.get_init_ecard(df_X, ml_boundaries)

        validation_idx = False
        if type(validation_X) != type(None):
            assert validation_X.shape[0] == validation_Y.shape[0]
            df_valY, df_valy, df_valy_binary = self.check_label(validation_Y)
            validation_X = self.get_cross_features(validation_X)
            df_valX_bins = pd.DataFrame()
            for col_, bins_ in self.blocks.items():
                idata = pd.cut(validation_X.loc[:, col_].fillna(0), bins=bins_)
                df_valX_bins[col_] = idata
            validation_idx = True

        log_step("start model iterative optimization ...")
        best_auc = -999
        best_insurance_auc = -999
        best_card = init_card
        for i,tree_bins in enumerate(ml_boundaries):
            if i>self.n_estimators:
                continue
            sample_idx = df_X.sample(
                frac=1.0, replace=True, weights=sample_weight, random_state=i
            ).sample(frac=self.sample_frac, replace=False, random_state=i).index
            df_woe,x = woe.get_woe_card(df_X.loc[sample_idx], df_Y.loc[sample_idx], tree_bins)
            clf_lr = LogisticRegression(**self.params_lr)
            clf_lr.fit(x, df_y_binary.loc[sample_idx], sample_weight=sample_weight.loc[sample_idx])
            clf_lr.col_name = x.columns
            add_card = self.get_score_card(clf_lr, df_woe)
            cur_card = self.get_cards_merge(best_card, add_card,
                                            cur_weight=self.cur_card_index / (self.cur_card_index + 1),
                                            add_weight=1.0 / (self.cur_card_index + 1))
            if 'local'==self.optimize_type:
                idx_ = sample_idx
            else:
                idx_ = df_X_bins.index
            df_pre_score = self.calc_score(cur_card, df_X_bins.loc[idx_], is_woe_feature = True)
            predict_ = -1*df_pre_score
            train_auc = self.score_model.get_auc(predict_, df_y_binary.loc[idx_].copy(), pre_target=1)[0]
            train_info = "train_auc={}".format(round(train_auc, 4))
            if self.is_best_bagging and (train_auc < best_auc):
                vote = False
            else:
                best_auc = train_auc
                vote = True
            if ('fee_got' in df_Y.columns) and ('report_fee' in df_Y.columns):
                train_insurance_auc = \
                    self.score_model.get_insurance_auc(predict_, df_Y.loc[idx_]["fee_got"], df_Y.loc[idx_]["report_fee"])[0]
                train_info = "{}, train_insurance_auc={}".format(train_info, round(train_insurance_auc, 4))
                if train_insurance_auc >= best_insurance_auc:
                    best_insurance_auc = train_insurance_auc
                    vote = True
            if vote:
                self.cur_card_index += 1
                best_card = cur_card

            validation_info=None
            if validation_idx and vote and (i%validation_step==0):
                df_pre_score = self.calc_score(cur_card, df_valX_bins, is_woe_feature=True)
                predict_ = -1 * df_pre_score
                validation_auc = self.score_model.get_auc(predict_, df_valy_binary.copy(), pre_target=1)[0]
                validation_info = "validation_auc={}".format(round(validation_auc, 4))
                if ('fee_got' in df_valY.columns) and ('report_fee' in df_valY.columns):
                    validation_insurance_auc = self.score_model.get_insurance_auc(predict_, df_valY["fee_got"], df_valY["report_fee"], )[0]
                    validation_info = "{}, validation_insurance_auc={}".format(validation_info,round(validation_insurance_auc,4))
            log_step("step_{}:\t{}\t{}".format(i+1,train_info,validation_info))
        self.score_ecard = best_card
        self.score_lower = best_card.groupby("field_").score_.min().sum()
        self.score_upper = best_card.groupby("field_").score_.max().sum()

    def fit_parallar(self, df_X, df_Y, validation_X:pd.DataFrame=None, validation_Y:pd.DataFrame=None, sample_weight=None, validation_step=1):
        assert df_X.shape[0] == df_Y.shape[0]
        df_Y, df_y, df_y_binary= self.check_label(df_Y)
        if type(sample_weight)==type(None):
            sample_weight=df_y*0+1

        log_step("start model fitting ...")
        df_X = self.calc_base_card(df_X, df_Y, df_y, df_y_binary, sample_weight)
        ml_boundaries = self.get_ml_boundaries(df_X, df_y, sample_weight=sample_weight)
        random.shuffle(ml_boundaries)
        init_card, df_X_bins = self.get_init_ecard(df_X, ml_boundaries)

        validation_idx = False
        if type(validation_X) != type(None):
            assert validation_X.shape[0] == validation_Y.shape[0]
            df_valY, df_valy, df_valy_binary = self.check_label(validation_Y)
            validation_X = self.get_cross_features(validation_X)
            df_valX_bins = pd.DataFrame()
            for col_, bins_ in self.blocks.items():
                idata = pd.cut(validation_X.loc[:, col_].fillna(0), bins=bins_)
                df_valX_bins[col_] = idata
            validation_idx = True

        log_step("start model iterative optimization ...")
        def fit_card(i,x_,y_,y_binary_,weight_,tree_bins_,return_dict):
            df_woe, x = woe.get_woe_card(x_, y_, tree_bins_)
            clf_lr = LogisticRegression(**self.params_lr)
            clf_lr.fit(x, y_binary_, weight_)
            clf_lr.col_name = x.columns
            add_card = self.get_score_card(clf_lr, df_woe)
            return_dict[i] = add_card

        return_dict = Manager().dict()
        jobs = []
        for i, tree_bins_ in enumerate(ml_boundaries):
            if i > self.n_estimators:
                continue
            sample_idx = df_X.sample(
                frac=1.0, replace=True, weights=sample_weight, random_state=i
            ).sample(frac=self.sample_frac, replace=False, random_state=i).index
            x_ = df_X.loc[sample_idx]
            y_ = df_Y.loc[sample_idx]
            y_binary_ = df_y_binary.loc[sample_idx]
            weight_ = sample_weight.loc[sample_idx]
            p = Process(target=fit_card, args=(i,x_,y_,y_binary_,weight_,tree_bins_,return_dict))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()

        best_auc = -999
        best_insurance_auc = -999
        best_card = init_card
        for add_card in return_dict.values():
            cur_card = self.get_cards_merge(best_card, add_card,
                                            cur_weight=self.cur_card_index / (self.cur_card_index + 1),
                                            add_weight=1.0 / (self.cur_card_index + 1))
            if 'local'==self.optimize_type:
                idx_ = sample_idx
            else:
                idx_ = df_X_bins.index
            df_pre_score = self.calc_score(cur_card, df_X_bins.loc[idx_], is_woe_feature = True)
            predict_ = -1*df_pre_score
            train_auc = self.score_model.get_auc(predict_, df_y_binary.loc[idx_].copy(), pre_target=1)[0]
            train_info = "train_auc={}".format(round(train_auc, 4))
            if self.is_best_bagging and (train_auc < best_auc):
                vote = False
            else:
                best_auc = train_auc
                vote = True
            if ('fee_got' in df_Y.columns) and ('report_fee' in df_Y.columns):
                train_insurance_auc = \
                    self.score_model.get_insurance_auc(predict_, df_Y.loc[idx_]["fee_got"], df_Y.loc[idx_]["report_fee"])[0]
                train_info = "{}, train_insurance_auc={}".format(train_info, round(train_insurance_auc, 4))
                if train_insurance_auc >= best_insurance_auc:
                    best_insurance_auc = train_insurance_auc
                    vote = True
            if vote:
                self.cur_card_index += 1
                best_card = cur_card

            validation_info=None
            if validation_idx and vote and (i%validation_step==0):
                df_pre_score = self.calc_score(cur_card, df_valX_bins, is_woe_feature=True)
                predict_ = -1 * df_pre_score
                validation_auc = self.score_model.get_auc(predict_, df_valy_binary.copy(), pre_target=1)[0]
                validation_info = "validation_auc={}".format(round(validation_auc, 4))
                if ('fee_got' in df_valY.columns) and ('report_fee' in df_valY.columns):
                    validation_insurance_auc = self.score_model.get_insurance_auc(predict_, df_valY["fee_got"], df_valY["report_fee"], )[0]
                    validation_info = "{}, validation_insurance_auc={}".format(validation_info,round(validation_insurance_auc,4))
            log_step("step_{}:\t{}\t{}".format(i+1,train_info,validation_info))
        self.score_ecard = best_card
        self.score_lower = best_card.groupby("field_").score_.min()
        self.score_upper = best_card.groupby("field_").score_.max()

    def check_label(self, df_label):
        df_Y=df_label.copy()
        if df_Y.shape[-1] == 1:
            df_Y.columns = ['label']
        if 'label' not in df_Y.columns:
            df_Y['label'] = df_Y.iloc[:,0]
        df_y=df_Y.label.astype(int)
        if df_y.unique().size>2:
            df_y_binary = df_y.apply(lambda x: 1 if x>0 else 0)
        else:
            df_y_binary = df_y
        df_Y['label']=df_y_binary
        ## test---
        if 'label_binary' in df_Y.columns:
            df_y_binary = df_Y["label_binary"]
        ## ---end
        return df_Y, df_y, df_y_binary

    def calc_base_card(self,df_X, df_Y, df_y, df_y_binary, sample_weight):
        clf_base_tree = DecisionTreeClassifier(**self.params_base_tree)
        clf_base_tree.fit(df_X, df_y, sample_weight=sample_weight)
        if hasattr(clf_base_tree, 'estimators_'):
            pass
        else:
            clf_base_tree.estimators_ = [clf_base_tree]
        tree_boundaries, cross_fields_boundaries = rf_bolcks.get_randomforest_blocks(clf_base_tree, col_name=df_X.columns, cross_hierarchy=self.cross_hierarchy)
        tree_bins, cross_fields_bins = tree_boundaries[0], cross_fields_boundaries[0]
        self.calc_cross_boundaries(cross_fields_bins)
        df_X = self.get_cross_features(df_X)
        for icol in df_X.columns:
            if 'ext-' not in icol:
                continue
            else:
                value_ = [-np.inf,np.inf]
                value_.extend(df_X[icol].unique()[1:-1])
                value_.sort()
                tree_bins.update({icol:value_})
        base_woe, x = woe.get_woe_card(df_X, df_Y, tree_bins)
        clf_lr = LogisticRegression(**self.params_lr)
        clf_lr.fit(x, df_y_binary, sample_weight=sample_weight)
        clf_lr.col_name = x.columns

        predict_ = clf_lr.predict_proba(x)[:, 1:].sum(axis=1)
        train_auc = self.score_model.get_auc(pd.DataFrame(predict_), df_y_binary.copy(), pre_target=1)[0]
        log_step("Init train_auc={}".format(round(train_auc, 4)))

        base_card = self.get_score_card(clf_lr, base_woe)
        self.init_cards.append(base_card)
        return df_X

    def calc_cross_boundaries(self, boundaries):
        '''

        :param boundaries: 默认按重要度由大到小排序的字段分箱
        :return:
        '''
        if len(boundaries) > 1:
            return
        init_ext = self.feature_ext_info.get('df_ext',pd.DataFrame())
        init_boundaries = self.feature_ext_info.get('boundaries_ext',{})
        boundaries = boundaries.update(init_boundaries)
        df_ext = pd.DataFrame(columns=['id_'])
        for col_, bins_ in boundaries.items():
            df_tmp = pd.cut([], bins=bins_).value_counts().sort_index().reset_index().rename(
                columns={'index': col_, 0: 'id_'})
            df_ext = df_ext.merge(df_tmp, how='outer', on='id_')
        df_ext['id_'] = range(len(df_ext))

        for i, j in itertools.product(boundaries.keys(), boundaries.keys()):
            if i==j:
                continue
            if i not in df_ext.columns:
                continue
            if j not in df_ext.columns:
                continue
            col_='ext-{}-{}'.format(i,j)
            if col_ in init_ext.columns:
                df_tmp = init_ext.copy()
                df_tmp['tmp_'] = df_tmp[[i, j]].astype(str).apply(lambda x: '-'.join(x), axis=1)
                df_tmp = df_tmp[['tmp_',col_]].drop_duplicates()
            else:
                df_tmp = pd.DataFrame(df_ext[[i,j]].astype(str).apply(lambda x: '-'.join(x), axis=1).drop_duplicates())
                df_tmp.columns=['tmp_']
                df_tmp[col_] = range(len(df_tmp))
            df_ext['tmp_'] = df_ext[[i,j]].astype(str).apply(lambda x: '-'.join(x), axis=1)
            df_ext = df_ext.join(df_tmp.set_index('tmp_'),on='tmp_',how='inner')
        if 'tmp_' in df_ext.columns:
            del df_ext['tmp_']
        self.feature_ext_info = {'df_ext':df_ext,'boundaries_ext':boundaries}

    def get_cross_features(self, df_data):
        df_X_ext = self.feature_ext_info.get('df_ext')
        boundaries_ext = self.feature_ext_info.get('boundaries_ext')
        if not(boundaries_ext):
            return df_data
        if len(boundaries_ext)<2:
            return df_data
        df_X = df_data.copy()
        df_tmp = pd.DataFrame()
        for k,bv in boundaries_ext.items():
            df_tmp[k]=pd.cut(df_X[k],bins=bv).astype(str)
        for icol in df_X_ext.columns:
            if 'ext-' not in icol:
                continue
            col_ = icol[4:].split('-')
            df_tmp['tmp_'] = df_tmp[col_].apply(lambda x: '-'.join(x), axis=1)
            df_X_ext['tmp_'] = df_X_ext[col_].astype(str).apply(lambda x: '-'.join(x), axis=1)
            df_ext_tmp = df_X_ext[['tmp_',icol]].drop_duplicates()
            df_tval = pd.merge(df_tmp,df_ext_tmp.set_index('tmp_'),how='inner',left_on='tmp_',right_index=True)[icol]
            assert len(df_tval)==len(df_X), (len(df_tval),len(df_X))
            df_X[icol] = df_tval
        return df_X

    def get_score_card(self,clf_lr,df_woe):
        coef_dict = dict(zip(clf_lr.col_name, clf_lr.coef_[0]))
        init_score = self.score_model.score_offset
        base_score = self.score_model.score_factor * clf_lr.intercept_[0]
        woe_col = [i for i in df_woe.columns if 'woe' in i]
        get_coef_summary = lambda x: np.sum([coef_dict.get(x['field_'] + '_' + i) * x[i] for i in woe_col])
        df_woe['score_'] = self.score_model.score_factor * df_woe.apply(get_coef_summary, axis=1)
        df_field_card = df_woe[['field_', 'bins_', 'boundary_', 'size_', 'score_']]
        df_base_card = pd.DataFrame(
            [['init_base_score', pd.Interval(-np.inf, np.inf, closed='right'), np.inf, -1, init_score],
             ['init_model_score', pd.Interval(-np.inf, np.inf, closed='right'),np.inf,  -1, base_score]
             ], columns=['field_', 'bins_', 'boundary_', 'size_', 'score_'])
        df_card = df_field_card.append(df_base_card, ignore_index=True)
        return df_card

    def get_ml_boundaries(self, df_X, df_y, sample_weight):
        if self.features_model =='rf':
            clf_rf = RandomForestClassifier(**self.params_rf)
            clf_rf.fit(df_X, df_y, sample_weight=sample_weight)
            rf_report = classification_report(df_y, clf_rf.predict(df_X))
            log_step("\nRF-report: \n {}".format(rf_report))
            rf_boundaries, _ = rf_bolcks.get_randomforest_blocks(clf_rf, col_name=df_X.columns)
            return rf_boundaries
        if self.features_model =='xgb':
            clf_xgb = XGBClassifier(**self.params_xgb)
            clf_xgb.fit(df_X, df_y, sample_weight=sample_weight)
            xgb_report = classification_report(df_y, clf_xgb.predict(df_X))
            log_step("\nXGB-report: \n {}".format(xgb_report))
            xgb_boundaries = xgb_bolcks.get_xgboost_blocks(clf_xgb, col_name=df_X.columns)
            return xgb_boundaries

    def get_init_ecard(self, df_X, ext_boundaries_list):
        boundaries_list = []
        if len(ext_boundaries_list)>0:
            boundaries_list.extend(ext_boundaries_list)
        for icard in self.init_cards:
            base_date=icard.groupby('field_').boundary_.agg(lambda x:sorted(set([-np.inf,np.inf]+list(x))) if len(x)>2 else None)
            base_boundaries = base_date[base_date.notna()].to_dict()
            if len(base_boundaries) > 0:
                boundaries_list.append(base_boundaries)
        boundaries = self.get_boundaries_merge(boundaries_list)
        self.blocks = boundaries

        len_=len(boundaries)
        bins_list=[]
        df_X_bins = pd.DataFrame()
        for i, (col, bins) in enumerate(boundaries.items()):
            progress_bar(i,len_-1)
            if col not in df_X.columns:
                log_step(" ------ {} column not exists, ignore!")
                continue
            idata = pd.cut(df_X.loc[:, col].fillna(0), bins=bins)
            df_X_bins[col] = idata
            data_bin = idata.value_counts()
            df_bin = pd.DataFrame(data_bin).sort_index().reset_index()
            df_bin.columns = ['bins_','size_']
            df_bin.insert(loc=0, column='field_', value=col)
            df_bin.insert(loc=2, column='boundary_', value=bins[1:])
            bins_list.append(df_bin)
        df_init_ecard = pd.concat(bins_list).reset_index(drop=True)
        df_base_card = pd.DataFrame(
            [['init_base_score', pd.Interval(-np.inf, np.inf, closed='right'), np.inf,-1],
             ['init_model_score', pd.Interval(-np.inf, np.inf, closed='right'), np.inf, -1]
             ], columns=['field_', 'bins_', 'boundary_', 'size_'])
        df_card = df_init_ecard.append(df_base_card, ignore_index=True)
        df_card['score_']=0

        cur_card = df_card
        for icard_ in self.init_cards:
            if self.cur_card_index==0:
                cur_card = self.get_cards_merge(cur_card, icard_, cur_weight=0, add_weight=1.0)
            else:
                cur_card = self.get_cards_merge(cur_card, icard_,
                                                cur_weight=self.cur_card_index / (self.cur_card_index + 1),
                                                add_weight=1.0 / (self.cur_card_index + 1))
            self.cur_card_index += 1

        return cur_card, df_X_bins

    def get_cards_merge(self, cur_card, add_card, cur_weight=0.5, add_weight=0.5):
        df_cur = cur_card.set_index(['field_', 'boundary_', 'size_'])
        df_add = cur_card.join(add_card.set_index('field_')[['bins_', 'score_']], on='field_', how='left',
                                rsuffix='_')
        idx = df_add.apply(
            lambda x: True if str(x['bins__']) != 'nan' and (x['bins_'].overlaps(x['bins__'])) else False, axis=1)
        df_add.loc[~idx, 'score__'] = 0
        df_add = df_add.groupby(['field_', 'boundary_', 'size_'])['score__'].sum()
        df_cur['score_'] = df_cur['score_']*cur_weight + df_add*add_weight
        return df_cur.reset_index()

    def get_boundaries_merge(self, boundaries_list):
        gl_boundaries={}
        for boundaries in boundaries_list:
            for k,v in boundaries.items():
                if k in gl_boundaries:
                    lv = gl_boundaries.get(k)
                    cv = list(set(v+lv))
                    cv.sort()
                    gl_boundaries.update({k:cv})
                else:
                    gl_boundaries.update({k: v})
        return gl_boundaries

    def calc_score(self, df_card, df_data: pd.DataFrame, is_woe_feature=False):
        df_score = pd.DataFrame()
        if is_woe_feature:
            pass
        else:
            bins_dict = df_card.groupby('field_').boundary_.agg(
                lambda x: sorted(set([-np.inf, np.inf] + list(x)))).to_dict()
        for field_ in df_card.field_.unique():
            if field_ in ['init_base_score','init_model_score']:
                continue
            _card = df_card[df_card.field_ == field_]
            _card["bins_"] = _card.bins_.astype(str)
            if is_woe_feature:
                _data = df_data[field_].astype(str)
            else:
                _data = pd.cut(df_data[field_].fillna(0), bins=bins_dict.get(field_, [-np.inf, np.inf])).astype(str)
            out = pd.merge(_data,_card.set_index("bins_"),how='left',left_on=_data.name,right_index=True)
            df_score[field_] = out['score_']
        df_score['init_base_score'] = df_card[df_card.field_ == 'init_base_score']['score_'].values[0]
        df_score['init_model_score'] = df_card[df_card.field_ == 'init_model_score']['score_'].values[0]
        score = df_score.sum(axis=1).apply(lambda x: round(x,2))
        return score

    def get_importance_(self):
        df_card_info = self.score_ecard.groupby("field_").agg(
            {'size_': [("weights", lambda x: list(x))],
             'score_': [("values", lambda x: list(x))]

             }).droplevel(0, 1)
        importance_ = df_card_info.apply(lambda x: get_weighted_std(x["values"], x["weights"]), axis=1)
        importance_ = (importance_/importance_.sum()).apply(lambda x:round(x,6))
        return importance_.sort_values(ascending=False)

    def predict(self, df_data):
        if self.cross_hierarchy>1:
            df_data = self.get_cross_features(df_data)
        df_score = self.calc_score(self.score_ecard,df_data)
        return df_score

    def predict_proba(self, df_data):
        df_score = self.predict(df_data)
        df_proba =df_score.apply(lambda x:self.score_model.score_to_probability(x))
        return df_proba

    def predict_hundred(self, df_data):
        '''
        百分制
        :param df_data:
        :return:
        '''
        df_score = self.predict(df_data)
        df_hundred =df_score.apply(lambda x:round((x-self.score_lower)/(self.score_upper-self.score_lower)*100,2))
        return df_hundred

    # 单车详细评分
    def get_single_score(self, data: dict, level_threshold=None):
        data = self.get_ext_features(data)
        score = 0
        score_detail = {}
        df_card = self.score_ecard
        for i, row in df_card.iterrows():
            field_ = row['field_']
            bins_ = row['bins_']
            score_ = row['score_']
            # class_ = row['class_']
            if field_ in ['init_base_score', 'init_model_score']:
                v = 0
            else:
                v = data.get(field_)
            try:
                v = float(v)
            except:
                score = 0
                score_detail[field_] = '异常'
                break
            if not (v > -np.inf):
                v = 0
            if v in bins_:
                score = score + score_
                score_detail[field_] = score_
            else:
                pass

        # level
        score = round(score)
        level = -1
        total_meters = data.get('run_meters', 0)
        total_seconds = data.get('run_seconds', 0)
        if (level_threshold is not None) and (total_meters >= 2000000) and (total_seconds >= 10 * 3600):
            level = np.argwhere(np.sort(level_threshold + [score]) == score).min()

        out = {'score': score, 'level': level, 'score_detail': score_detail}
        return out

    def get_ext_features(self, data):
        if hasattr(self, 'feature_ext_info'):
            df_ext = self.feature_ext_info.get("df_ext")
            if type(df_ext)!=pd.DataFrame:
                return data
            if len(df_ext)<1:
                return data
            ext_columns = [i for i in df_ext.columns if 'ext-' in i]
            for i in ext_columns:
                colinfo = str(i).split('-')
                if 'ext' == colinfo[0]:
                    idx_equ = True
                    for icol in colinfo[1:]:
                        if icol not in df_ext.columns:
                            break
                        idx_equ = idx_equ & df_ext[icol].apply(lambda x: data.get(icol) in x).astype(int)
                    value_ = df_ext.loc[idx_equ, i].values
                    if len(value_) > 0:
                        data.update({i: value_[0]})
                    else:
                        data.update({i: 0})
        return data

    def init_check(self):
        if isinstance(self.init_cards,pd.DataFrame):
            col_ = [i for i in self.init_cards.columns if 'ext-'==i[:4]]
            if len(col_)>0:
                df_ext = self.feature_ext_info.get('df_ext')
                for i in col_:
                    if i not in df_ext.columns:
                        log_step("no detail info for cross field:{}".format(i))
                        break

if __name__ == '__main__':
    df_valid = pd.read_csv("data/train_test_data.csv")
    df_train_data = df_valid[df_valid['train_test_tag'] == '训练集'].fillna(0)
    df_test_data = df_valid[df_valid['train_test_tag'] == '测试集'].fillna(0)
    features_col = ['trip_avg_meters',
                    'trip_avg_seconds', 'trip_avg_distance', 'high_meters_ratio',
                    'province_meters_ratio', 'high_trip_cnt_ratio',
                    'province_trip_cnt_ratio', 'curvature_g2_trip_meters_ratio',
                    'ng_23_6_seconds_ratio', 'ng_23_6_trip_cnt_ratio', 'daily_run_kmeters',
                    'daily_run_hours', 'daily_trip_cnt', 'daily_nohigh_kmeters',
                    'daily_ng_23_6_hours', 'trip_long_cnt_ratio', 'day_high_meters_ratio',
                    'ng_province_meters_ratio', 'morn_6_10_seconds_ratio',
                    'dusk_17_20_seconds_ratio', 'ng_23_6_avg_speed', 'morn_6_10_avg_speed',
                    'dusk_17_20_avg_speed', 'low_speed_seconds_ratio',
                    'low_speed_block_cnt_ratio', 'week_1_5_seconds_ratio',
                    'geohash4_top10_meters_ratio', 'trip_r30m_cnt_ratio',
                    'common_line_top30_cnt_ratio', 'ratio_meitan', 'ratio_gangtie', 'ratio_shashi',
                    'ratio_kuaidi', 'ratio_nonglinmufu', 'ratio_jiadian', 'ratio_jixie',
                    'ratio_qiche', 'ratio_fengdian', 'ratio_other'
                    ]
    df_X = df_train_data[features_col]
    df_Y = df_train_data[['label', 'label_ordinary',
                          'label_serious', 'label_major', 'label_devastating', 'label_8w','fee_got','report_fee']]
    df_Y['label']=df_Y.apply(lambda x:x['label'] if x["report_fee"]<5000 else 2,axis=1)
    ecard = ECardModel(
        kwargs_rf={'n_estimators':20},
        kwargs_xgb={'n_estimators':2},
        cross_hierarchy=3,
        is_best_bagging=True,
        features_model='xgb',
        optimize_type='local',
    )


    # 初始加载河北模型进行微调 -------------------
    import dill
    def load_local_model(model_path):
        model = dill.load(open(model_path, "rb"))
        clf = model.get('model')
        score_card = model.get('score_card')
        score_bins = model.get('score_bins')
        get_card_level = model.get('get_card_level')
        func_calc_level = lambda x: get_card_level(x["card_score"], x["run_meters"], x["run_seconds"], score_bins)

        return clf, func_calc_level


    model_file = 'data/score_card_model_local_major_hebeibeijing_v3.1.0.pkl'
    clf_hebei, func_calc_level = load_local_model(model_path=model_file)
    ecard.init_cards.append(clf_hebei.score_ecard)
    ecard.feature_ext_info = clf_hebei.feature_ext_info
    ### ----------------------------------------------

    ecard.fit(df_X, df_Y,df_X, df_Y,sample_weight=df_Y['label']+1, validation_step=1)
    print(ecard.get_importance_())
    print(ecard.predict(df_X))
    print(ecard.predict_hundred(df_X))
    data = df_test_data.loc[0].to_dict()
    print(ecard.get_single_score(data=data, level_threshold=[-np.inf,400,536,550,600,np.inf]))
    print("""
    3.calc score 优化为predict，提高速度
    4.woe计算优化
    5.并行优化
    """)