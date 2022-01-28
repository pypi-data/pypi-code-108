# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/6 00:11
Desc:
'''


import numpy as np
import pandas as pd

## 评分体系
class ScoreCardModel:
    def __init__(self):
        self.load_score_alpha()

    def load_score_alpha(self, odds=1 / 2, bScore=600, addScore=-30):
        '''
            bScore = offset - factor*ln(odds)
            bScore + addScore = offset - factor*ln(2*odds)
        :param odds: 坏好比
        :param bScore: 基础score分
        :param addScore: 评分变动值
        :return: bScore = offset - factor*ln(odds)
        '''

        self.score_factor = addScore / np.log(2)
        self.score_offset = bScore - addScore * np.log(odds) / np.log(2)

    def probability_to_score(self, bad_prob, eps=1e-5):
        '''
            逾期概率转换为评分
        :param bad_prob: 逾期概率
        :return: bScore = offset - factor*ln(odds)
        '''

        odds = max(bad_prob, eps) / max(1 - bad_prob, eps)
        score = self.score_offset + self.score_factor * np.log(odds)
        return int(round(score))

    def score_to_probability(self, score, eps=1e-5):
        '''
            评分转换为逾期概率
        :param score: 信用评分
        :return: bScore = offset - factor*ln(odds) -->bad_prob
        '''
        score_factor = eps if self.score_factor==0 else self.score_factor
        odds = np.e**((score - self.score_offset)/(score_factor))
        odds = -1+eps if odds == -1 else odds
        bad_prob = 1.00*odds/(1+odds)
        return bad_prob

    @classmethod
    def get_auc(cls, df_pre, df_label, df_weight=None, pre_target=1):
        '''
        功能: 计算KS值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_label: 一维数组或series，代表真实的标签{0,1}
        :param df_weight: 一维数组或series，代表样本权重
        :param pre_target: 'auc': auc值，'crossdens': TPR&FPR
        :return:
        '''
        if isinstance(df_pre, pd.DataFrame):
            df_pre = df_pre.iloc[:,0]
        if isinstance(df_label, pd.DataFrame):
            df_label = df_label.iloc[:,0]
        if isinstance(df_weight, pd.DataFrame):
            df_weight = df_weight.iloc[:,0]

        if type(df_weight)==type(None):
            df_weight = df_pre*np.array(0)+1
        assert len(df_pre) == len(df_weight) == len(df_label)
        df_pre.reset_index(drop=True, inplace=True)
        df_weight.reset_index(drop=True, inplace=True)
        df_label.reset_index(drop=True, inplace=True)

        df_label = df_label.apply(lambda x: 1 if x == pre_target else 0)
        if df_label.unique().size < 2:
            return None, None
        # 按照预测概率从大到小排序作为阈值
        crossfreq = pd.crosstab(df_pre, df_label, df_weight, aggfunc=sum).fillna(0).sort_index(ascending=False)
        crossdens = crossfreq.cumsum(axis=0) / crossfreq.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        fpr = crossdens.loc[:, 'fpr']
        tpr = crossdens.loc[:, 'tpr']
        auc = np.trapz(y=tpr, x=fpr)
        return auc, crossdens

    @classmethod
    def get_insurance_auc(cls, df_pre, df_got_fee, df_report_fee, df_weight=None):
        '''
        功能: 计算auc值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_got_fee: 一维数组或series，代表已赚保费
        :param df_report_fee: 一维数组或series，代表赔付额
        :param df_weight:
        :return: 'auc': auc值，'crossdens': TPR&FPR
        '''
        if isinstance(df_pre, pd.DataFrame):
            df_pre = df_pre.iloc[:,0]
        if isinstance(df_got_fee, pd.DataFrame):
            df_got_fee = df_got_fee.iloc[:,0]
        if isinstance(df_report_fee, pd.DataFrame):
            df_report_fee = df_report_fee.iloc[:,0]
        if isinstance(df_weight, pd.DataFrame):
            df_weight = df_weight.iloc[:,0]

        if type(df_weight)==type(None):
            df_weight = df_pre*np.array(0)+1
        assert len(df_pre) == len(df_weight) == len(df_got_fee) == len(df_report_fee)
        df_pre.reset_index(drop=True, inplace=True)
        df_weight.reset_index(drop=True, inplace=True)
        df_got_fee.reset_index(drop=True, inplace=True)
        df_report_fee.reset_index(drop=True, inplace=True)

        df_data = pd.concat([df_got_fee, df_report_fee],axis=1, ignore_index=True)
        df_data = df_data.mul(df_weight,axis=0).fillna(0)
        df_data.columns = ['got_fee', 'report_fee']
        order_index = df_pre.reset_index(drop=True).sort_values(ascending=False).index
        crossdens = df_data.loc[order_index,:].cumsum(axis=0) / df_data.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        fpr = crossdens.loc[:, 'fpr']
        tpr = crossdens.loc[:, 'tpr']
        auc = np.trapz(y=tpr, x=fpr)
        return auc, crossdens

    @classmethod
    def get_ks(cls, df_pre, df_label, df_weight=None, pre_target=1):
        '''
        功能: 计算KS值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_label: 一维数组或series，代表真实的标签
        :param df_weight: 一维数组或series，代表样本权重
        :param pre_target:
        :return:
            'ks': KS值
            'crossdens': 好坏客户累积概率分布以及其差值gap
        '''
        if isinstance(df_pre, pd.DataFrame):
            df_pre = df_pre.iloc[:, 0]
        if isinstance(df_label, pd.DataFrame):
            df_label = df_label.iloc[:, 0]
        if isinstance(df_weight, pd.DataFrame):
            df_weight = df_weight.iloc[:, 0]

        if type(df_weight) == type(None):
            df_weight = df_pre * np.array(0) + 1
        assert len(df_pre) == len(df_weight) == len(df_label)
        df_pre.reset_index(drop=True, inplace=True)
        df_weight.reset_index(drop=True, inplace=True)
        df_label.reset_index(drop=True, inplace=True)

        df_label = df_label.apply(lambda x: 1 if x == pre_target else 0)
        if df_label.unique().size < 2:
            return None, None
        # 按照预测概率从大到小排序
        crossfreq = pd.crosstab(df_pre, df_label, df_weight, aggfunc=sum).fillna(0).sort_index(ascending=False)
        crossdens = crossfreq.cumsum(axis=0) / crossfreq.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        crossdens['gap'] = abs(crossdens['fpr'] - crossdens['tpr'])
        ks = crossdens[crossdens['gap'] == crossdens['gap'].max()]
        return ks, crossdens

    @classmethod
    def get_insurance_ks(cls, df_pre, df_got_fee, df_report_fee, df_weight=None):
        '''
        功能: 计算auc值，输出对应分割点和累计分布函数曲线图
        :param df_pre: 一维数组或series，代表模型得分
        :param df_got_fee: 一维数组或series，代表已赚保费
        :param df_report_fee: 一维数组或series，代表赔付额
        :param df_weight:
        :return: 'auc': auc值，'crossdens': TPR&FPR
        '''
        if isinstance(df_pre, pd.DataFrame):
            df_pre = df_pre.iloc[:,0]
        if isinstance(df_got_fee, pd.DataFrame):
            df_got_fee = df_got_fee.iloc[:,0]
        if isinstance(df_report_fee, pd.DataFrame):
            df_report_fee = df_report_fee.iloc[:,0]
        if isinstance(df_weight, pd.DataFrame):
            df_weight = df_weight.iloc[:,0]

        if type(df_weight)==type(None):
            df_weight = df_pre * np.array(0) + 1
        assert len(df_pre) == len(df_weight) == len(df_got_fee) == len(df_report_fee)
        df_pre.reset_index(drop=True, inplace=True)
        df_weight.reset_index(drop=True, inplace=True)
        df_got_fee.reset_index(drop=True, inplace=True)
        df_report_fee.reset_index(drop=True, inplace=True)

        df_data = pd.concat([df_got_fee, df_report_fee],axis=1, ignore_index=True)
        df_data = df_data.mul(df_weight,axis=0).fillna(0)
        df_data.columns = ['got_fee', 'report_fee']
        order_index = df_pre.reset_index(drop=True).sort_values(ascending=False).index
        crossdens = df_data.loc[order_index,:].cumsum(axis=0) / df_data.sum()
        crossdens.columns = ['fpr', 'tpr']
        crossdens.name = 'pre_threshold'
        crossdens['gap'] = abs(crossdens['fpr'] - crossdens['tpr'])
        ks = crossdens[crossdens['gap'] == crossdens['gap'].max()]
        return ks, crossdens

    @classmethod
    def get_auc_report(cls, df_pre, df_label, df_got_fee, df_report_fee, df_subset_identity=None, df_weight=None,
                       pre_target=1, subset_weight='balance'):
        if type(df_subset_identity) == type(None):
            df_subset_identity = df_pre.apply(lambda _: '全量')
        if type(df_weight) == type(None):
            if 'balance' == subset_weight:
                dict_ = (df_subset_identity.shape[0] / df_subset_identity.value_counts()).to_dict()
                dict_.update({"其他": 1})
                df_weight = df_subset_identity.apply(lambda x: dict_.get(x, 1))
            else:
                df_weight = df_pre * np.array(0) + 1
        assert len(df_pre) == len(df_got_fee) == len(df_report_fee) == len(df_subset_identity) == len(df_weight), print(
            len(df_pre), len(df_got_fee), len(df_report_fee), len(df_subset_identity), len(df_weight))
        df_pre.reset_index(drop=True, inplace=True)
        df_got_fee.reset_index(drop=True, inplace=True)
        df_report_fee.reset_index(drop=True, inplace=True)
        df_weight.reset_index(drop=True, inplace=True)
        df_subset_identity.reset_index(drop=True, inplace=True)

        auc_report_all = cls.get_auc(df_pre, df_label, df_weight, pre_target)[0]
        auc_fee_all = cls.get_insurance_auc(df_pre, df_got_fee * 0 + 15000, df_report_fee, df_weight)[0]
        index_ = ['全量']
        data_ = [[len(df_pre), auc_report_all, auc_fee_all]]

        if df_subset_identity.unique().size > 1:
            for ii in df_subset_identity.unique():
                idx = df_subset_identity[df_subset_identity == ii].index
                auc_report = cls.get_auc(df_pre.loc[idx], df_label.loc[idx], df_weight.loc[idx], pre_target)[0]
                auc_fee = \
                cls.get_insurance_auc(df_pre.loc[idx], df_got_fee.loc[idx], df_report_fee.loc[idx], df_weight.loc[idx])[0]
                data_.append([len(idx), auc_report, auc_fee])
                index_.append(ii)
        df_report = pd.DataFrame(data_, columns=['样本量', '出险率_auc', '赔付率_auc'], index=index_).sort_values("样本量",
                                                                                                         ascending=False)
        return df_report

    @classmethod
    def get_auc_report2(cls, df, by_field='subset_identity', weight_field=None, pre_target=1, subset_weight='balance',
                        fix_fee_got=True):
        assert 'predict' in df.columns
        assert 'label' in df.columns
        assert 'fee_got' in df.columns
        assert 'report_fee' in df.columns
        df_pre = df.predict
        df_label = df.label
        df_got_fee = df.fee_got
        df_report_fee = df.report_fee
        if fix_fee_got:
            df_got_fee = df_got_fee * 0 + 1000
        if by_field in df.columns:
            df_subset_identity = df[by_field]
        else:
            df_subset_identity = None
        if weight_field in df.columns:
            df_weight = df[weight_field]
        else:
            df_weight = None
        df_report = cls.get_auc_report(df_pre, df_label, df_got_fee, df_report_fee, df_subset_identity, df_weight,
                                   pre_target, subset_weight)

        return df_report

# 评分校准
def get_calibration_score(raw_score):
    pass

if __name__ == '__main__':
    model_score = ScoreCardModel()
    score = model_score.probability_to_score(0.5)
    print(score)