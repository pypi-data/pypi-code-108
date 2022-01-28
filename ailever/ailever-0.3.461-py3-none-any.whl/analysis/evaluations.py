import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class RegressionMetricUnit:
    """
    metrics.explained_variance_score(y_true, y_pred)
    metrics.max_error(y_true, y_pred) #ME
    metrics.mean_absolute_error(y_true, y_pred) # MAE
    metrics.mean_squared_error(y_true, y_pred)  # MSE
    metrics.mean_absolute_percentage_error(y_true, y_pred)
    metrics.mean_tweedie_deviance(y_true, y_pred)
    metrics.median_absolute_error(y_true, y_pred) 
    metrics.r2_score(y_true, y_pred)

    n = X.shape[0]
    p = X.shape[1]

    y_pred = model.predict(X)
    sse = np.power((y_true - y_pred), 2)
    sst = np.power((y_true - np.mean(y_true)), 2)
    ssr = np.power((y_pred - np.mean(y_true)), 2)
    
    pseudo_r2 = np.divide(ssr, sst)
    normal_r2 = 1 - np.divide(sse, sst)
    adjusted_r2 = 1 - np.multiply((1 - normal_r2), np.divide(n-1, n-p-1))
    vif = np.divide(1, (1-adjusted_r2))

    classic_eval_matrix = pd.DataFrame()
    classic_eval_matrix['FeatureImportance'] = importance
    classic_eval_matrix['PseudoRSquare'] = pseudo_r2
    classic_eval_matrix['RSquare'] = normal_r2
    classic_eval_matrix['AdjustedRSquare'] = adjusted_r2
    classic_eval_matrix['VIFactor'] = vif
    """


    @staticmethod
    def MSE(y_true, y_pred):
        import numpy as np
        metric = np.mean(np.power((y_true - y_pred), 2))
        return metric

    @staticmethod
    def RMSE(y_true, y_pred):
        import numpy as np
        metric = np.sqrt(np.mean(np.power((y_true - y_pred), 2)))
        return metric

    @staticmethod
    def MAE(y_true, y_pred):
        import numpy as np
        metric = np.mean(np.abs(y_true - y_pred))
        return metric

    @staticmethod
    def MAPE(y_true, y_pred):
        import numpy as np
        metric = np.mean(np.abs(np.divide(y_true - y_pred, y_true)))
        return metric

    @staticmethod
    def R2(y_true, y_pred):
        from sklearn.metrics import r2_score
        metric = r2_score(y_true, y_pred)
        return metric


class ClassificationMetricUnit:
    """
    metrics.balanced_accuracy_score(y_true, y_pred)
    metrics.hamming_loss(y_true, y_pred)
    metrics.zero_one_loss(y_true, y_pred)
    """

    @staticmethod
    def ACC(y_true, y_pred):
        from sklearn.metrics import accuracy_score
        metric = accuracy_score(y_true, y_pred)
        return metric

    @staticmethod
    def PPV(y_true, y_pred):
        from sklearn.metrics import precision_score
        metric = precision_score(y_true, y_pred, average='micro')
        return metric

    @staticmethod
    def TPR(y_true, y_pred):
        from sklearn.metrics import recall_score
        metric = recall_score(y_true, y_pred, average='micro')
        return metric

    @staticmethod
    def F1(y_true, y_pred):
        from sklearn.metrics import f1_score
        metric = f1_score(y_true, y_pred, average='micro')
        return metric
    
    @staticmethod
    def Fbeta(y_true, y_pred, beta=2):
        from sklearn.metrics import fbeta_score
        metric = fbeta_score(y_true, y_pred, beta=beta, average='micro')
        return metric

    @staticmethod
    def MCC(y_true, y_pred):
        from sklearn.metrics import matthews_corrcoef
        metric = matthews_corrcoef(y_true, y_pred)
        return metric

    @staticmethod
    def JI(y_true, y_pred):
        from sklearn.metrics import jaccard_score
        metric = jaccard_score(y_true, y_pred, average='micro')
        return metric

class ClusteringMetricUnit:
    pass


class Evaluation(RegressionMetricUnit, ClassificationMetricUnit, ClusteringMetricUnit):
    def __init__(self, subject):
        r"""
        from ailever.analysis import Evaluation

        Evaluation.target_class_evaluation(y_true, y_pred)
        Evaluation.roc_curve(y_true, y_prob)
        Evaluation.pr_curve(y_true, y_prob)
        Evaluation.feature_importance(X, y_pred)
        Evaluation.information_value(X, y_true)
        Evaluation.decision_tree(X, y_true)
        Evaluation.imputation(X, new_X)
        Evaluation.imbalance(X, new_X)
        Evaluation.linearity(X, y_true)

        Evaluation('classification').about(y_true, y_pred)
        Evaluation('regression').about(y_true, y_pred)
        Evaluation('clustering').about(X, new_X)
        Evaluation('manifolding').about(X, new_X)
        Evaluation('filtering').about(observed_features, filtered_features)
        """
        self.subject = subject
        self.subjects = dict()

    def about(self, **kwargs):
        return getattr(self, self.subject)(**kwargs)

    def classification(self, y_true, y_pred):
        return self

    def regression(self, y_true, y_pred):
        return self

    def clustering(self, X):
        return self
 
    @staticmethod
    def decision_tree(table, min_samples_leaf=100, min_samples_split=30, max_depth=2):
        from sklearn.tree import DecisionTreeClassifier, export_graphviz
        import graphviz

        frame = table.copy()
        X = frame.loc[:, frame.columns != 'target']
        y = frame.loc[:, frame.columns == 'target']
        feature_names = frame.columns.copy()
        feature_names = feature_names.drop('target')
        target_names = frame.attrs['target_names']

        criterions = ['gini', 'entropy']
        splitters = ['best', 'random']

        decision_tree = DecisionTreeClassifier(
            criterion=criterions[0],
            splitter=splitters[1],
            min_samples_leaf=min_samples_leaf,
            min_samples_split=min_samples_split,
            max_depth=max_depth,
        )
        decision_tree.fit(X, y)

        dot_data=export_graphviz(decision_tree,
                                 out_file=None,
                                 feature_names=feature_names,
                                 class_names=target_names,
                                 filled=True,
                                 rounded=True,
                                 special_characters=True)

        print('- FEATURES:', feature_names)
        print('- TARGET  :', target_names)
        return graphviz.Source(dot_data)


    @staticmethod
    def information_value(y_true, y_pred):
        pass
    
    @staticmethod
    def feature_property(model, X, y_true, permutation=False, visual_on=True):
        import pandas as pd
        from matplotlib import pyplot as plt
        from sklearn.inspection import permutation_importance
        from statsmodels.stats.outliers_influence import variance_inflation_factor

        model.fit(X, y_true)

        # feature importance
        if permutation:
            importance = permutation_importance(model, X, y_true, n_repeats=30, random_state=0).importances_mean
        else:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = model.coef_
            else:
                return

        # variance inflation factor
        vif = [variance_inflation_factor(X, i) for i in range(X.shape[1])]
        normal_r2 = 1 - np.divide(1, np.array(vif))

        if visual_on:
            _, axes = plt.subplots(3,1, figsize=(25, 7*max(int(X.shape[1]/20), 1)))
            axes[0].barh([x for x in range(len(importance))], importance)
            axes[0].set_title('FeatureImportance')
            axes[1].barh([x for x in range(len(normal_r2))], normal_r2)
            axes[1].set_title('Linearity:R-Square')
            axes[2].barh([x for x in range(len(vif))], vif)
            axes[2].set_title('Linearity:VarianceInflationFactor')
            plt.tight_layout()

        classic_eval_matrix = pd.DataFrame()
        classic_eval_matrix['FeatureImportance'] = importance
        classic_eval_matrix['Linearity:R-Square'] = normal_r2
        classic_eval_matrix['Linearity:VIFactor'] = vif
        return classic_eval_matrix


    @staticmethod
    def target_class_evaluation(y_true, y_pred):
        from sklearn.metrics import confusion_matrix

        conf_matrix = confusion_matrix(y_true, y_pred)

        metrics = dict()
        for metric in ['P', 'N', 'PP', 'PN'] + ['TP', 'FP', 'TN', 'FN']+['PPV', 'FDR', 'FOR', 'NPV']+['TPR', 'FPR', 'FNR', 'TNR']+['LR+', 'LR-']+['MK', 'DOR']+['F1', 'FM']+['MCC', 'JI']+['ACC', 'Prevalence', 'BA', 'BM', 'PT']:
            metrics[metric] = dict()

        for true_idx in range(conf_matrix.shape[0]):
            metrics['P'][true_idx] = conf_matrix[true_idx, :].sum()
            metrics['N'][true_idx] = conf_matrix[:, :].sum() - conf_matrix[true_idx, :].sum()
            metrics['Prevalence'][true_idx] = metrics['P'][true_idx]/(metrics['P'][true_idx] + metrics['N'][true_idx])

        for pred_idx in range(conf_matrix.shape[1]):
            # Positive
            metrics['PP'][pred_idx] = conf_matrix[:, pred_idx].sum() 
            # Negative
            metrics['PN'][pred_idx] = conf_matrix[:, :].sum() - conf_matrix[:, pred_idx].sum() 
            # hit
            metrics['TP'][pred_idx] = conf_matrix[pred_idx, pred_idx] 
            # type I error, false alarm, overestimation
            metrics['FP'][pred_idx] = conf_matrix[:, pred_idx].sum() - conf_matrix[pred_idx, pred_idx] 
            # correct rejection
            metrics['TN'][pred_idx] = conf_matrix[:, :].sum() - conf_matrix[pred_idx, :].sum() - conf_matrix[:, pred_idx].sum() + conf_matrix[pred_idx, pred_idx] 
            # type II error, miss, underestimation
            metrics['FN'][pred_idx] = conf_matrix[pred_idx, :].sum() - conf_matrix[pred_idx, pred_idx] 

        for true_idx in range(conf_matrix.shape[0]):
            pred_idx = true_idx
            # True positive rate (TPR), recall, sensitivity (SEN), probability of detection, hit rate, power
            metrics['TPR'][true_idx] = metrics['TP'][pred_idx]/metrics['P'][true_idx] if metrics['P'][true_idx] != 0 else np.inf
            # False positive rate (FPR), probability of false alarm, fall-out
            metrics['FPR'][true_idx] = metrics['FP'][pred_idx]/metrics['N'][true_idx] if metrics['N'][true_idx] != 0 else np.inf
            # False negative rate (FNR), miss rate
            metrics['FNR'][true_idx] = metrics['FN'][pred_idx]/metrics['P'][true_idx] if metrics['P'][true_idx] != 0 else np.inf
            # True negative rate (TNR), specificity (SPC), selectivity
            metrics['TNR'][true_idx] = metrics['TN'][pred_idx]/metrics['N'][true_idx] if metrics['N'][true_idx] != 0 else np.inf
            # Accuracy (ACC)
            metrics['ACC'][true_idx] = (metrics['TP'][pred_idx] + metrics['TN'][pred_idx])/(metrics['P'][true_idx] + metrics['N'][true_idx]) if metrics['P'][true_idx] + metrics['N'][true_idx] != 0 else np.inf
            # Balanced accuracy (BA)
            metrics['BA'][true_idx] = metrics['TPR'][true_idx]/metrics['TNR'][true_idx] if metrics['TNR'][true_idx] != 0 else np.inf
            # Informedness, bookmaker informedness (BM)
            metrics['BM'][true_idx] = metrics['TPR'][true_idx] + metrics['TNR'][true_idx] - 1 
            # Prevalence threshold (PT)
            metrics['PT'][true_idx] = (np.sqrt(metrics['TPR'][true_idx]*metrics['FPR'][true_idx])-metrics['FPR'][true_idx])/(metrics['TPR'][true_idx] - metrics['FPR'][true_idx]) if not any([np.isinf(metrics['TPR'][true_idx]), np.isinf(metrics['FPR'][true_idx])]) and (metrics['TPR'][true_idx] != metrics['FPR'][true_idx]) else np.nan

        for pred_idx in range(conf_matrix.shape[1]):
            true_idx = pred_idx
            # Positive predictive value (PPV), precision
            metrics['PPV'][pred_idx] = metrics['TP'][pred_idx]/metrics['PP'][pred_idx] if metrics['PP'][pred_idx] != 0 else 1.0
            # False discovery rate (FDR)
            metrics['FDR'][pred_idx] = metrics['FP'][pred_idx]/metrics['PP'][pred_idx] if metrics['PP'][pred_idx] != 0 else np.inf
            # False omission rate (FOR)
            metrics['FOR'][pred_idx] = metrics['FN'][pred_idx]/metrics['PN'][pred_idx] if metrics['PN'][pred_idx] != 0 else np.inf
            # Negative predictive value (NPV)
            metrics['NPV'][pred_idx] = metrics['TN'][pred_idx]/metrics['PN'][pred_idx] if metrics['PN'][pred_idx] != 0 else 1.0
            # Markedness (MK), deltaP (Δp)
            metrics['MK'][pred_idx] = metrics['PPV'][pred_idx] + metrics['NPV'][pred_idx] - 1 
            # F1 score
            metrics['F1'][pred_idx] = (2*metrics['TP'][pred_idx])/(2*metrics['TP'][pred_idx] + metrics['FP'][pred_idx] + metrics['FN'][pred_idx]) if 2*metrics['TP'][pred_idx] + metrics['FP'][pred_idx] + metrics['FN'][pred_idx] != 0 else np.inf
            # Fowlkes–Mallows index (FM)
            metrics['FM'][pred_idx] = np.sqrt(metrics['PPV'][pred_idx]*metrics['TPR'][true_idx]) if not any([np.isinf(metrics['PPV'][pred_idx]), np.isinf(metrics['TPR'][true_idx])]) else np.nan
            # Matthews correlation coefficient (MCC)
            metrics['MCC'][pred_idx] = np.sqrt(metrics['TPR'][true_idx]*metrics['TNR'][true_idx]*metrics['PPV'][pred_idx]*metrics['NPV'][pred_idx]) - np.sqrt(metrics['FNR'][true_idx]*metrics['FPR'][true_idx]*metrics['FOR'][pred_idx]*metrics['FDR'][pred_idx]) if not any([np.isinf(metrics['TPR'][true_idx]), np.isinf(metrics['TNR'][true_idx]), np.isinf(metrics['PPV'][true_idx]), np.isinf(metrics['NPV'][true_idx]), np.isinf(metrics['FNR'][true_idx]), np.isinf(metrics['FPR'][true_idx]), np.isinf(metrics['FOR'][true_idx]), np.isinf(metrics['FDR'][true_idx])]) else np.nan
            # Threat score (TS), critical success index (CSI), Jaccard index
            metrics['JI'][pred_idx] = metrics['TP'][pred_idx] / (metrics['TP'][pred_idx] + metrics['FN'][pred_idx] + metrics['FP'][pred_idx]) if metrics['TP'][pred_idx] + metrics['FN'][pred_idx] + metrics['FP'][pred_idx] != 0 else np.inf

        for true_idx in range(conf_matrix.shape[0]):
            # Positive likelihood ratio (LR+)
            metrics['LR+'][true_idx] = metrics['TPR'][true_idx]/metrics['FPR'][true_idx] if metrics['FPR'][true_idx] != 0 else np.inf
            # Negative likelihood ratio (LR−)
            metrics['LR-'][true_idx] = metrics['FNR'][true_idx]/metrics['TNR'][true_idx] if metrics['TNR'][true_idx] != 0 else np.inf
            # Diagnostic odds ratio (DOR)
            metrics['DOR'][true_idx] = metrics['LR+'][true_idx]/metrics['LR-'][true_idx] if not any([np.isinf(metrics['LR+'][true_idx] ), np.isinf(metrics['LR-'][true_idx] ), metrics['LR-'][true_idx] == 0]) else np.nan

        evaluation = pd.DataFrame(columns=list(range(conf_matrix.shape[0])))
        for name, metric in metrics.items():
            metric_ = dict()
            for class_idx, metric_value in metric.items():
                metric_[class_idx] = [metric_value]
            metric_ = pd.DataFrame(metric_).rename(index={0:name})
            evaluation = evaluation.append(metric_)
        return evaluation
 
    @staticmethod
    def roc_curve(y_true, y_prob, num_threshold=11, predicted_condition=None, visual_on=False):
        from sklearn.metrics import confusion_matrix, auc

        # y_preds[target_class][threshold] : y_pred with nd.array type
        _y_preds = dict() 
        additional_instance = np.abs(np.unique(y_true)).sum()
        for target_class in np.unique(y_true):
            _y_preds[target_class] = dict()
            
            thresholds = list()
            for threshold in np.linspace(0, 1, num_threshold):
                thresholds.append(threshold)
                _y_preds[target_class][threshold] = np.where(y_prob[:, target_class]>=threshold, target_class, additional_instance)

        # y_preds[target_class] : y_pred with pd.DataFrame type by thresholds
        y_preds = dict()
        for target_class, pred_by_class in _y_preds.items():
             y_preds[target_class] = pd.DataFrame(pred_by_class)
        
        # Positive
        # _FPR_TPRs[target_class][threshold] : fpr, tpr
        _FPR_TPRs = dict()
        for target_class, y_pred in y_preds.items():
            _FPR_TPRs[target_class] = dict()
            for threshold in thresholds:
                _FPR_TPRs[target_class][threshold] = Evaluation.target_class_evaluation(y_true, y_pred[threshold]).loc[['FPR', 'TPR']][target_class].values

        # FPR_TPRs[target_class] : fpr, tpr by threshold
        FPR_TPRs = dict()
        P_AUCs = dict()
        for target_class, fpr_tpr in _FPR_TPRs.items():
            roc_frame = pd.DataFrame(fpr_tpr)
            FPR_TPRs[target_class] = roc_frame.copy().rename(index={0:'FPR', 1:'TPR'})
            P_AUCs[target_class] = auc(roc_frame.loc[0].values, roc_frame.loc[1].values)

        # Negative
        # _FNR_TNRs[target_class][threshold] : fnr, tnr
        _FNR_TNRs = dict()
        for target_class, y_pred in y_preds.items():
            _FNR_TNRs[target_class] = dict()
            for threshold in thresholds:
                _FNR_TNRs[target_class][threshold] = Evaluation.target_class_evaluation(y_true, y_pred[threshold]).loc[['FNR', 'TNR']][target_class].values

        # FNR_TNRs[target_class] : fnr, tnr by threshold
        FNR_TNRs = dict()
        N_AUCs = dict()
        for target_class, fnr_tnr in _FNR_TNRs.items():
            roc_frame = pd.DataFrame(fnr_tnr)
            FNR_TNRs[target_class] = roc_frame.copy().rename(index={0:'FNR', 1:'TNR'})
            N_AUCs[target_class] = auc(roc_frame.loc[0].values, roc_frame.loc[1].values)
        
        if predicted_condition is None:
            if visual_on:
                fig = plt.figure(figsize=(25,7)); layout=(1,2); axes = dict()
                axes[0] = plt.subplot2grid(layout, (0,0), fig=fig)
                axes[1] = plt.subplot2grid(layout, (0,1), fig=fig)
                for (P_target_class, FPR_TPR), P_AUC, (N_target_class, FNR_TNR), N_AUC in zip(FPR_TPRs.items(), P_AUCs.values(), FNR_TNRs.items(), N_AUCs.values()) :
                    axes[0].plot(FPR_TPR.loc['FPR'].values, FPR_TPR.loc['TPR'].values, marker='o', label=str(P_target_class)+' | '+str(round(P_AUC, 2)))
                    axes[1].plot(FNR_TNR.loc['FNR'].values, FNR_TNR.loc['TNR'].values, marker='o', label=str(N_target_class)+' | '+str(round(N_AUC, 2)))

                axes[0].plot([0, 1], [0, 1], 'k--')
                axes[0].set_title('FPR/TPR')
                axes[0].set_xlabel('Fall-Out')
                axes[0].set_ylabel('Recall')
                axes[0].legend()
                axes[1].plot([0, 1], [0, 1], 'k--')
                axes[1].set_title('FNR/TNR')
                axes[1].set_xlabel('Miss-Rate')
                axes[1].set_ylabel('Selectivity')
                axes[1].legend()
            return (FPR_TPRs, P_AUCs), (FNR_TNRs, N_AUCs)

        if predicted_condition: # Positive
            if visual_on:
                plt.figure(figsize=(25,7))
                for (target_class, FPR_TPR), P_AUC in zip(FPR_TPRs.items(), P_AUCs.values()):
                    plt.plot(FPR_TPR.loc['FPR'].values, FPR_TPR.loc['TPR'].values, marker='o', label=str(target_class)+' | '+str(round(P_AUC, 2)))
                plt.plot([0, 1], [0, 1], 'k--')
                plt.title('FPR/TPR')
                plt.xlabel('Fall-Out')
                plt.ylabel('Recall')
                plt.legend()
            return FPR_TPRs, P_AUCs
        else:                   # Negative
            if visual_on:
                plt.figure(figsize=(25,7))
                for (target_class, FNR_TNR), N_AUC in zip(FNR_TNRs.items(), N_AUCs.values()):
                    plt.plot(FNR_TNR.loc['FNR'].values, FNR_TNR.loc['TNR'].values, marker='o', label=str(target_class)+' | '+str(round(N_AUC, 2)))
                plt.plot([0, 1], [0, 1], 'k--')
                plt.title('FNR/TNR')
                plt.xlabel('Miss-Rate')
                plt.ylabel('Selectivity')
                plt.legend()
            return FNR_TNRs, N_AUCs

    @staticmethod
    def pr_curve(y_true, y_prob, num_threshold=11, predicted_condition=None, visual_on=False):
        from sklearn.metrics import confusion_matrix, auc

        # y_preds[target_class][threshold] : y_pred with nd.array type
        _y_preds = dict() 
        additional_instance = np.abs(np.unique(y_true)).sum()
        for target_class in np.unique(y_true):
            _y_preds[target_class] = dict()
            
            thresholds = list()
            for threshold in np.linspace(0, 1, num_threshold):
                thresholds.append(threshold)
                _y_preds[target_class][threshold] = np.where(y_prob[:, target_class]>=threshold, target_class, additional_instance)

        # y_preds[target_class] : y_pred with pd.DataFrame type by thresholds
        y_preds = dict()
        for target_class, pred_by_class in _y_preds.items():
             y_preds[target_class] = pd.DataFrame(pred_by_class)
        
        # Positive
        # _PPV_TPRs[target_class][threshold] : ppv, tpr
        _PPV_TPRs = dict()
        for target_class, y_pred in y_preds.items():
            _PPV_TPRs[target_class] = dict()
            for threshold in thresholds:
                _PPV_TPRs[target_class][threshold] = Evaluation.target_class_evaluation(y_true, y_pred[threshold]).loc[['PPV', 'TPR']][target_class].values

        # PPV_TPRs[target_class] : ppv, tpr by threshold
        PPV_TPRs = dict()
        P_AUCs = dict()
        for target_class, ppv_tpr in _PPV_TPRs.items():
            pr_frame = pd.DataFrame(ppv_tpr)
            PPV_TPRs[target_class] = pr_frame.copy().rename(index={0:'PPV', 1:'TPR'})
            P_AUCs[target_class] = auc(pr_frame.loc[1].values, pr_frame.loc[0].values)

        # Negative
        # _NPV_TNRs[target_class][threshold] : npv, tnr
        _NPV_TNRs = dict()
        for target_class, y_pred in y_preds.items():
            _NPV_TNRs[target_class] = dict()
            for threshold in thresholds:
                _NPV_TNRs[target_class][threshold] = Evaluation.target_class_evaluation(y_true, y_pred[threshold]).loc[['NPV', 'TNR']][target_class].values

        # NPV_TNRs[target_class] : npv, tnr by threshold
        NPV_TNRs = dict()
        N_AUCs = dict()
        for target_class, npv_tnr in _NPV_TNRs.items():
            pr_frame = pd.DataFrame(npv_tnr)
            NPV_TNRs[target_class] = pr_frame.copy().rename(index={0:'NPV', 1:'TNR'})
            N_AUCs[target_class] = auc(pr_frame.loc[1].values, pr_frame.loc[0].values)
        
        if predicted_condition is None:
            if visual_on:
                fig = plt.figure(figsize=(25,7)); layout=(1,2); axes = dict()
                axes[0] = plt.subplot2grid(layout, (0,0), fig=fig)
                axes[1] = plt.subplot2grid(layout, (0,1), fig=fig)
                for (P_target_class, PPV_TPR), P_AUC, (N_target_class, NPV_TNR), N_AUC in zip(PPV_TPRs.items(), P_AUCs.values(), NPV_TNRs.items(), N_AUCs.values()) :
                    axes[0].plot(PPV_TPR.loc['TPR'].values, PPV_TPR.loc['PPV'].values, marker='o', label=str(P_target_class)+' | '+str(round(P_AUC, 2)))
                    axes[1].plot(NPV_TNR.loc['TNR'].values, NPV_TNR.loc['NPV'].values, marker='o', label=str(N_target_class)+' | '+str(round(N_AUC, 2)))

                axes[0].plot([0, 1], [1, 0], 'k--')
                axes[0].set_title('TPR/PPV')
                axes[0].set_xlabel('Recall')
                axes[0].set_ylabel('Precision')
                axes[0].legend()
                axes[1].plot([0, 1], [1, 0], 'k--')
                axes[1].set_title('TNR/NPV')
                axes[1].set_xlabel('Selectivity')
                axes[1].set_ylabel('NegativePredictiveValue')
                axes[1].legend()
            return (PPV_TPRs, P_AUCs), (NPV_TNRs, N_AUCs)

        if predicted_condition: # Positive
            if visual_on:
                plt.figure(figsize=(25,7))
                for (target_class, PPV_TPR), P_AUC in zip(PPV_TPRs.items(), P_AUCs.values()):
                    plt.plot(PPV_TPR.loc['TPR'].values, PPV_TPR.loc['PPV'].values, marker='o', label=str(target_class)+' | '+str(round(P_AUC, 2)))
                plt.plot([0, 1], [1, 0], 'k--')
                plt.title('TPR/PPV')
                plt.xlabel('Recall')
                plt.ylabel('Precision')
                plt.legend()
            return PPV_TPRs, P_AUCs
        else:                   # Negative
            if visual_on:
                plt.figure(figsize=(25,7))
                for (target_class, NPV_TNR), N_AUC in zip(NPV_TNRs.items(), N_AUCs.values()):
                    plt.plot(NPV_TNR.loc['TNR'].values, NPV_TNR.loc['NPV'].values, marker='o', label=str(target_class)+' | '+str(round(N_AUC, 2)))
                plt.plot([0, 1], [1, 0], 'k--')
                plt.title('TNR/NPV')
                plt.xlabel('Selectivity')
                plt.ylabel('NegativePredictiveValue')
                plt.legend()
            return NPV_TNRs, N_AUCs

    def imputation(self):
        pass

    def imbalance(self):
        pass

    def reduction(self):
        pass

    def linearity(self):
        pass


