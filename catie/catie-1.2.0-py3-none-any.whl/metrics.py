#!/usr/bin/python
# metrics.py
# par Jianfei Zhang (jianfei.zhang@live.ca) le 26 janvier 2022

import numpy as np
import pandas as pd
from IPython.display import display
import plotly.express as px
import math
from sklearn.metrics import confusion_matrix, roc_auc_score
import matplotlib as mpl
from matplotlib import pyplot as plt

class CAT:
    def __init__(
        self,
        col_ID,
        col_tied_ID,
        col_cohort,
        col_true_label,
        col_pred_label,
        col_pred_proba,
        sig=None,
        alpha=0.7,
    ):
        
        (
            self.col_ID,
            self.col_tied_ID,
            self.col_cohort,
            self.col_true_label,
            self.col_pred_label,
            self.col_pred_proba,
        ) = (col_ID, col_tied_ID, col_cohort, col_true_label, col_pred_label, col_pred_proba)
        self.sig = sig
        self.alpha = alpha
        self.dark_mode = False
    
    def init_data(self, df):
        self.data = df
        for col in [
            self.col_ID,
            self.col_tied_ID,
            self.col_cohort,
            self.col_true_label,
            self.col_pred_label,
            self.col_pred_proba,
        ]:
            if col in self.data.index.names:
                self.data = self.data.reset_index(col)
    
    def set_proba(self, pred_proba):
        self.data[self.col_pred_proba] = pred_proba       

    def get_auc(self):
        self.auc = roc_auc_score(self.data[self.col_true_label], self.data[self.col_pred_proba])
        print("AUC = {:.3f}".format(self.auc))
    
    def get_sen_spe(self, cut):
        self.data[self.col_pred_label] = [
            1 if i >= cut else 0 for i in self.data[self.col_pred_proba]
        ]
        CM = confusion_matrix(
            self.data[self.col_true_label], self.data[self.col_pred_label], labels=[0, 1]
        )
        tn = CM[0][0]
        tp = CM[1][1]
        fp = CM[0][1]
        fn = CM[1][0]
        p = tp + fn
        n = tn + fp
        sen = tp / p
        spe = tn / n
        print(
            "sensitivity = {:.3f} ({}/{})\nspecificity = {:.3f} ({}/{})\n".format(
                sen, tp, p, spe, tn, n
            )
        )
        self.binary_metric = [sen, tp, p, spe, tn, n]

    def get_res(self):
        Labels, Preds, Cohorts, num_tests, sum_preds = [], [], [], [], []
        tiedIDs = self.data[self.col_tied_ID].unique().tolist()
        for i in tiedIDs:
            lbl = self.data[self.data[self.col_tied_ID] == i][self.col_true_label].unique()
            preds = self.data[self.data[self.col_tied_ID] == i][self.col_pred_label].values
            gps = self.data[self.data[self.col_tied_ID] == i][self.col_cohort].unique()[
                0
            ]
            Labels.append(lbl[0])
            Preds.append(preds)
            Cohorts.append(gps)
            num_tests.append(len(preds))
            sum_preds.append(sum(preds))
        d = pd.DataFrame(
            data={
                self.col_tied_ID: tiedIDs,
                self.col_true_label: Labels,
                self.col_pred_label: Preds,
                self.col_cohort: Cohorts,
                "num_tests": num_tests,
                "sum_preds": sum_preds,
            }
        ).set_index(self.col_tied_ID)
        d["Score"] = (d["sum_preds"] - (1 - d[self.col_true_label]) * d["num_tests"]).abs()
        d["Acc"] = (d["sum_preds"] - (1 - d[self.col_true_label]) * d["num_tests"]).abs() / d["num_tests"]
        for i in [0, 1]:
            d.loc[d[self.col_true_label] == i, "total_num_tests_cls"] = len(
                d[d[self.col_true_label] == i]
            )
        d["p_cls"] = d["num_tests"] / d["total_num_tests_cls"]
        d["E_cls"] = -d["p_cls"] * np.log(d["p_cls"])
        d["E_cls_Acc"] = d["E_cls"] * d["Acc"]
        return d

    def split(self, df, label):
        return df[df[self.col_true_label] == label]

    def weighting(self, d_sig, d_non_sig, coef_sig):
        if len(d_sig) + len(d_non_sig) == 0:
            print("wrong input sig!")
        elif len(d_sig) * len(d_non_sig) != 0:
            score = coef_sig * d_sig["A"].sum() / len(d_sig) + (
                1 - coef_sig
            ) * d_non_sig["A"].sum() / len(d_non_sig)
        else:
            if len(d_sig) == 0:
                score = d_non_sig["A"].sum() / len(d_non_sig)
            if len(d_non_sig) == 0:
                score = d_sig["A"].sum() / len(d_sig)
        return score

    def get_Tmean(self, TSen, TSpe, beta):
        return math.sqrt((1 + beta ** 2) * (TSen * TSpe) / ((beta ** 2) * TSen + TSpe))

    def score(self, beta=1):
        self.d_res = self.get_res()
        d_cohort = self.d_res.groupby(by=[self.col_cohort, self.col_true_label])[
            ["E_cls", "E_cls_Acc"]
        ].sum()
        d_cohort = d_cohort.reset_index([self.col_cohort, self.col_true_label])
        d_cohort["A"] = d_cohort["E_cls_Acc"] / d_cohort["E_cls"]
        
        if self.sig == None:
            d_pos, d_neg = self.split(d_cohort, 1), self.split(d_cohort, 0)
            self.TSen, self.TSpe = d_pos["A"].sum() / len(d_pos), d_neg[
                "A"
            ].sum() / len(d_neg)
            self.TScore = self.TScore(self.TSen, self.TSpe, beta)
        else:
            d_sig = d_cohort[d_cohort[self.col_cohort].isin(self.sig)]
            d_non_sig = d_cohort[~d_cohort[self.col_cohort].isin(self.sig)]
            d_sig_pos, d_sig_neg = self.split(d_sig, 1), self.split(d_sig, 0)
            d_non_sig_pos, d_non_sig_neg = self.split(d_non_sig, 1), self.split(
                d_non_sig, 0
            )
            self.TSpe = self.weighting(d_sig_neg, d_non_sig_neg, self.alpha)
            logit = 1 / (1 + math.exp(0.5 - self.alpha))
            self.TSen = self.weighting(d_sig_pos, d_non_sig_pos, 1 - logit)
            self.Tmean = self.get_Tmean(self.TSen, self.TSpe, beta)
        print("CATSensitivity = {:.3f} (alpha = {:.2f})\nCATSpecificity = {:.3f} (alpha = {:.2f})".format(self.TSen, self.alpha, self.TSpe, self.alpha))
        print("CATmean = {:.3f} (beta = {:.1f})\n".format(self.Tmean, beta))
        
    def score_cohort(self):
        self.all_res = []
        for s in self.data[self.col_cohort].unique():
            d_project = self.data[self.data[self.col_cohort] == s]
            actuals = d_project[self.col_true_label]
            predictions = d_project[self.col_pred_label]
            if len(d_project[self.col_true_label].unique()) > 1:
                CM = confusion_matrix(actuals, predictions, labels=[0, 1])
                tn = CM[0][0]
                tp = CM[1][1]
                fp = CM[0][1]
                fn = CM[1][0]
                print(
                    "{}: 1/0, Sensitivity = {:.3f} ({}/{}), Specificity = {:.3f} ({}/{})".format(
                        s, tp / (tp + fn), tp, tp + fn, tn / (tn + fp), tn, tn + fp
                    )
                )
                rc = [s, '1/0', tp / (tp + fn), tp, tp + fn, tn / (tn + fp), tn, tn + fp]
            else:
                lbl = d_project[self.col_true_label].unique()[0]
                correction = len(
                    d_project[d_project[self.col_true_label] == d_project[self.col_pred_label]]
                )
                total = len(d_project)
                acc = correction / total
                print(
                    "{}: {}, accuracy = {:.3f} ({}/{})".format(
                        s, lbl, acc, correction, total
                    )
                )
                rc = [s, str(lbl), acc, correction, total]
            self.all_res.append(rc)

    def setup(self, fig):
        fig.update_yaxes(gridcolor=None, linecolor="grey")
        fig.update_xaxes(gridcolor=None, linecolor="grey")

        if self.dark_mode:
            fig.update_layout(
                {
                    "plot_bgcolor": "rgba(0, 0, 0, 0)",
                    "paper_bgcolor": "rgba(0, 0, 0, 0)",
                },
                margin=dict(l=0, r=20, b=0, t=30, pad=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            fig.layout.template = "plotly_dark"
        else:
            fig.update_layout(margin=dict(l=0, r=20, b=0, t=30, pad=0))
            fig.layout.template = "plotly_white"

    def plot_cohort_score(self, labels=[0, 1], num_occur=2):
        colors = [mpl.colors.rgb2hex(plt.cm.get_cmap("Dark2", 8)(i)) for i in range(8)]
        d_tag = self.d_res[self.d_res["num_tests"] >= num_occur]
        seq_score = [i for i in range(self.d_res["num_tests"].max() + 1)]
        d_tag = d_tag[d_tag[self.col_true_label].isin(labels)]
        d_tag = d_tag.sort_values(self.col_true_label).astype(str)
        fig = px.histogram(
            d_tag[["Score", self.col_true_label, self.col_cohort]],
            x="Score",
            color=self.col_true_label,
            color_discrete_sequence=colors,
            barmode="group",
            category_orders={"Score": seq_score[::-1]},
        )
        self.setup(fig)
        fig.update_yaxes(title="total # of individuals")
        fig.update_xaxes(
            title="# of a repeatedly tested individual's correctly predicted samples"
        )
        fig.show()

    def stat_proba(self):
        colors = [mpl.colors.rgb2hex(plt.cm.get_cmap("Dark2", 8)(i)) for i in range(8)]
        df = self.data.sort_values(self.col_true_label)
        fig = px.histogram(
            df[[self.col_true_label, self.col_pred_proba]],
            color=self.col_true_label,
            color_discrete_sequence=colors,
        )
        self.setup(fig)
        fig.update_yaxes(title="# of individuals")
        fig.update_xaxes(title="Predicted Probability")
        fig.show()

    def plot_proba(self):
        colors = [mpl.colors.rgb2hex(plt.cm.get_cmap("Dark2", 8)(i)) for i in range(8)]
        df = self.data.sort_values(self.col_true_label)
        df[self.col_true_label] = df[self.col_true_label].astype(str)
        fig = px.bar(
            df[[self.col_true_label, self.col_pred_proba]],
            x=df[self.col_ID],
            y=self.col_pred_proba,
            color=self.col_true_label,
            color_discrete_sequence=colors,
        )
        self.setup(fig)
        fig.update_yaxes(title='Predicted Probability')
        fig.update_xaxes(title=self.col_ID)
        fig.update_layout(height=1200)
        fig.show()
