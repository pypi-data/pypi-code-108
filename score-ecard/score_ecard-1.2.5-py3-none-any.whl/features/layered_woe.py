# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/11/5 22:08
Desc:
'''

import numpy as np
import pandas as pd
from score_ecard.util import progress_bar,log_cur_time
from multiprocessing import Pool


class WeightOfEvidence:
    def __init__(self,bad_target=1):
        self.bad_target = bad_target
        self.eps = 1e-4
        self.woe_card = None

    def fit(self,df_x,df_y):
        '''
        :param df_x: 特征字段
        :param df_y: 标签分类字段
        :return:
            返回woe详细信息
        '''
        self.cur_field = df_x.name or 'field'
        # |fields |bins |bad |good |bad_prob |good_prob |woe |iv
        bin = np.unique(df_x.drop_duplicates())
        good = np.array([np.logical_and(df_x == val, df_y != self.bad_target).sum() for val in bin])
        bad = np.array([np.logical_and(df_x == val, df_y == self.bad_target).sum() for val in bin])
        prob_good = good / float(np.sum(df_y != self.bad_target))
        prob_bad = bad / float(np.sum(df_y==self.bad_target))
        woe = np.log(np.maximum(prob_good,self.eps)/np.maximum(prob_bad,self.eps))
        iv = (prob_good-prob_bad)*woe
        df_info = pd.DataFrame(data=np.array([bin,good,bad,prob_good,prob_bad,woe,iv]).T,
                               columns=['bin','good','bad','good_prob','bad_prob','woe','iv'])
        df_info.insert(0, 'fields', self.cur_field)
        self.woe_card=df_info.fillna(0)

    def transform(self,x):
        card = self.woe_card
        if type(x) in (pd.DataFrame,pd.Series):
            df_x = pd.DataFrame(x)
            df_x.columns = ['bin']
            out = pd.merge(df_x, self.woe_card.set_index('bin'), how='left', left_on='bin', right_index=True)
        else:
            out = card[card.bin == x].woe
        return out

    def fit_transform(self,df_x,df_y):
        self.fit(df_x,df_y)
        out = self.transform(df_x)
        return out


class WeightOfFeeEvidence:
    def __init__(self,bad_target=1):
        self.bad_target = bad_target
        self.eps = 1e-4
        self.woe_card = None

    def fit(self,df_x,df_fee_got,df_report_fee):
        '''
        :param df_x: 特征字段
        :param df_fee_got: 已赚保费
        :param df_report_fee: 赔付金额
        :return:
            返回woe详细信息
        '''
        self.cur_field = df_x.name or 'field'
        # |fields |bins |bad |good |bad_prob |good_prob |woe |iv
        bin = np.unique(df_x.drop_duplicates())
        good = np.array([((df_x == val)*df_fee_got).sum() for val in bin])
        bad = np.array([((df_x == val)*df_report_fee).sum() for val in bin])
        prob_good = good / float(np.sum(df_fee_got))
        prob_bad = bad / float(np.sum(df_report_fee))
        woe = np.log(np.maximum(prob_good,self.eps)/np.maximum(prob_bad,self.eps))
        iv = (prob_good-prob_bad)*woe
        df_info = pd.DataFrame(data=np.array([bin,good,bad,prob_good,prob_bad,woe,iv]).T,
                               columns=['bin','get_fee','report_fee','get_fee_prob','report_fee_prob','woe','iv'])
        df_info.insert(0, 'fields', self.cur_field)
        self.woe_card=df_info.fillna(0)

    def transform(self,x):
        card = self.woe_card
        if type(x) in (pd.DataFrame,pd.Series):
            df_x = pd.DataFrame(x)
            df_x.columns = ['bin']
            out = pd.merge(df_x, self.woe_card.set_index('bin'), how='left', left_on='bin', right_index=True)
        else:
            out = card[card.bin == x].woe
        return out

    def fit_transform(self, df_x, df_fee_got, df_report_fee):
        self.fit(df_x, df_fee_got, df_report_fee)
        out = self.transform(df_x)
        return out

def get_woe_card_backups(df_X, df_Y, fields_bins):
    '''

    :param df_X:
    :param df_Y:
    :param fields_bins: 特征的分箱字典
    :return: 构建woe字典
    '''
    assert 'label' in df_Y.columns

    df_data = pd.DataFrame()
    woe_list = []
    len_=len(fields_bins)
    for i,(col, bins) in enumerate(fields_bins.items()):
        progress_bar(i,len_-1)
        bin_data = pd.cut(df_X.loc[:,col].fillna(0), bins=bins)
        # label1：是否出险
        woe1 = WeightOfEvidence()
        x1 = woe1.fit_transform(bin_data, df_Y["label"])
        df_data["{}_woe1".format(col)] = x1["woe"]
        card = woe1.woe_card
        card.columns = ['特征字段', '分箱', '无出险车辆数', '出险车辆数',
                        '无出险占比', '出险占比', 'woe1', 'iv1']
        card['车辆总数'] = card['无出险车辆数'] + card['出险车辆数']

        # label2：赔付率
        if ('fee_got' in df_Y.columns) and ('report_fee' in df_Y.columns):
            woe2 = WeightOfFeeEvidence()
            x = woe2.fit_transform(bin_data, df_Y["fee_got"], df_Y["report_fee"])
            df_data["{}_woe0".format(col)] = x["woe"]
            card2 = woe2.woe_card
            card[["已赚保费", "赔付金额", "已赚保费占比", "赔付金额占比", "woe0", "iv0"]] = card2[
                ['get_fee', 'report_fee', 'get_fee_prob', 'report_fee_prob', 'woe', 'iv']]

        # label3：是否有过赔付2k+
        if 'label_ordinary' in df_Y.columns:
            woe3 = WeightOfEvidence()
            x2 = woe3.fit_transform(bin_data, df_Y["label_ordinary"])
            df_data["{}_woe2".format(col)] = x2["woe"]
            card3 = woe3.woe_card
            card[["赔付车辆数", "无赔付车辆数", "赔付车辆占比", "无赔付车辆占比", "woe2", "iv2"]] = card3[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

        # label4：是否大事故1w+
        if 'label_serious' in df_Y.columns:
            woe4 = WeightOfEvidence()
            x3 = woe4.fit_transform(bin_data, df_Y["label_serious"])
            df_data["{}_woe3".format(col)] = x3["woe"]
            card4 = woe4.woe_card
            card[["重大事故车辆数", "非重大事故车辆数", "重大事故占比", "非重大事故占比", "woe3", "iv3"]] = card4[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

        # label5：是否重大事故5w+
        if 'label_major' in df_Y.columns:
            woe5 = WeightOfEvidence()
            x4 = woe5.fit_transform(bin_data, df_Y["label_major"])
            df_data["{}_woe4".format(col)] = x4["woe"]
            card5 = woe5.woe_card
            card[["特大事故车辆数", "非特大事故车辆数", "特大事故占比", "非特大事故占比", "woe4", "iv4"]] = card5[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

        # label6：是否特大事故20W'+
        if 'label_devastating' in df_Y.columns:
            woe5 = WeightOfEvidence()
            x5 = woe5.fit_transform(bin_data, df_Y["label_devastating"])
            df_data["{}_woe5".format(col)] = x5["woe"]
            card5 = woe5.woe_card
            card[["特大事故车辆数", "非特大事故车辆数", "特大事故占比", "非特大事故占比", "woe5", "iv5"]] = card5[
                ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

        rdata_ = pd.DataFrame(bin_data.value_counts().sort_index().index)
        rdata_.columns=['分箱']
        rdata_["阈值"] = bins[1:]
        card = pd.merge(card, rdata_, how='right', left_on='分箱', right_on='分箱')
        col_t_ = [i for i in card.columns if i !='分箱']
        card[col_t_] = card[col_t_].bfill().ffill()

        woe_list.append(card)
    woe_dict = pd.concat(woe_list).reset_index(drop=True)
    woe_dict.columns.name = 'idx'
    col = ['特征字段', '分箱', '阈值', '车辆总数'] + [i for i in woe_dict if 'woe' in i]+ [i for i in woe_dict if 'iv' in i]
    df_woe = woe_dict[col]
    df_woe.rename(columns={'特征字段':'field_', '分箱':'bins_', '阈值':'boundary_', '车辆总数':'size_'},inplace=True)
    return df_woe, df_data

def get_woe_card(df_X, df_Y, fields_bins):
    '''

    :param df_X:
    :param df_Y:
    :param fields_bins: 特征的分箱字典
    :return: 构建woe字典
    '''
    assert 'label' in df_Y.columns
    results = []
    p = Pool()
    for i,(col, bins) in enumerate(fields_bins.items()):
        df_x = df_X.loc[:, col].fillna(0)
        results.append(p.apply_async(get_woe_card_single, args=(df_x,df_Y,bins)))
    p.close()
    p.join()

    woe_list = []
    data_list = []
    for res in results:
        card_, data_ = res.get()
        woe_list.append(card_)
        data_list.append(data_)
    woe_dict = pd.concat(woe_list).reset_index(drop=True)
    woe_dict.columns.name = 'idx'
    col = ['特征字段', '分箱', '阈值', '车辆总数'] + [i for i in woe_dict if 'woe' in i]+ [i for i in woe_dict if 'iv' in i]
    df_woe = woe_dict[col]
    df_woe.rename(columns={'特征字段':'field_', '分箱':'bins_', '阈值':'boundary_', '车辆总数':'size_'},inplace=True)
    df_data = pd.concat(data_list,axis=1)
    return df_woe, df_data

def get_woe_card_single(df_x, df_Y, bins):
    '''

    :param df_x:
    :param df_Y:
    :param bins: 特征的分箱字典
    :return:
    '''
    df_data = pd.DataFrame()

    col = df_x.name
    bin_data = pd.cut(df_x, bins=bins)
    # label1：是否出险
    woe1 = WeightOfEvidence()
    woe1.fit(bin_data, df_Y["label"])
    card = woe1.woe_card
    card.columns = ['特征字段', '分箱', '无出险车辆数', '出险车辆数',
                    '无出险占比', '出险占比', 'woe1', 'iv1']
    card['车辆总数'] = card['无出险车辆数'] + card['出险车辆数']

    # label2：赔付率
    if ('fee_got' in df_Y.columns) and ('report_fee' in df_Y.columns):
        woe2 = WeightOfFeeEvidence()
        woe2.fit(bin_data, df_Y["fee_got"], df_Y["report_fee"])
        card2 = woe2.woe_card
        card[["已赚保费", "赔付金额", "已赚保费占比", "赔付金额占比", "woe0", "iv0"]] = card2[
            ['get_fee', 'report_fee', 'get_fee_prob', 'report_fee_prob', 'woe', 'iv']]

    # label3：是否有过赔付2k+
    if 'label_ordinary' in df_Y.columns:
        woe3 = WeightOfEvidence()
        woe3.fit(bin_data, df_Y["label_ordinary"])
        card3 = woe3.woe_card
        card[["赔付车辆数", "无赔付车辆数", "赔付车辆占比", "无赔付车辆占比", "woe2", "iv2"]] = card3[
            ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

    # label4：是否大事故1w+
    if 'label_serious' in df_Y.columns:
        woe4 = WeightOfEvidence()
        woe4.fit(bin_data, df_Y["label_serious"])
        card4 = woe4.woe_card
        card[["重大事故车辆数", "非重大事故车辆数", "重大事故占比", "非重大事故占比", "woe3", "iv3"]] = card4[
            ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

    # label5：是否重大事故5w+
    if 'label_major' in df_Y.columns:
        woe5 = WeightOfEvidence()
        woe5.fit(bin_data, df_Y["label_major"])
        card5 = woe5.woe_card
        card[["特大事故车辆数", "非特大事故车辆数", "特大事故占比", "非特大事故占比", "woe4", "iv4"]] = card5[
            ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

    # label6：是否特大事故20W'+
    if 'label_devastating' in df_Y.columns:
        woe5 = WeightOfEvidence()
        woe5.fit(bin_data, df_Y["label_devastating"])
        card5 = woe5.woe_card
        card[["特大事故车辆数", "非特大事故车辆数", "特大事故占比", "非特大事故占比", "woe5", "iv5"]] = card5[
            ['good', 'bad', 'good_prob', 'bad_prob', 'woe', 'iv']]

    rdata_ = pd.DataFrame(bin_data.value_counts().sort_index().index)
    rdata_.columns=['分箱']
    rdata_["阈值"] = bins[1:]
    card = pd.merge(card, rdata_, how='right', left_on='分箱', right_on='分箱')
    col_t_ = [i for i in card.columns if i !='分箱']
    card[col_t_] = card[col_t_].bfill().ffill()

    df_out = pd.DataFrame(bin_data).merge(card.set_index('分箱'), how='left', left_on=bin_data.name, right_index=True)
    for icol_ in df_out.columns:
        if 'woe' in icol_:
            df_data["{}_{}".format(col, icol_)] = df_out[icol_]
    return card, df_data