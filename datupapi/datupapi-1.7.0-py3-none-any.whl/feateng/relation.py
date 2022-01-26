import math
import os
import pandas as pd
import numpy as np
from datupapi.configure.config import Config
from sklearn.preprocessing import MinMaxScaler
import dowhy
from dowhy import CausalModel

class Relation(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def string_normalization(self, texto):
        tupla = (("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),(",", ""),(".", ""),(":", ""),(";", "")
                ,("-", ""),("¡", ""),("!", ""),("¿", ""),("?", "")
                ,("'", ""),("#", ""),("$", ""),("%", ""),("&", ""),("/", "_"),('<', ""),('>', ""),('[', "")
                ,(']', ""),('*', ""),('-', ""),('+', ""),('°', ""),('¬', ""),('{', ""),('}', ""),('\n', ""),('\t', "")
                ,('"',""),('«',""),('»',""),("@",""),(" ","_"))
        for a, b in tupla:
            texto = texto.replace(a, b)
        return texto    


    def min_max_scaler(self, data):
        """
        Scales the data with a Min Max scaler.
        
        :param data: Input dataframe used to train the models predictions.
 
        :return scalers: Array with the scalers for each feature.
        :return data_train: Normalized input dataframe.

        """
        scalers={}
        #data_train=data.iloc[:,n_features:].copy()
        data_train=data.copy()
        for j in data_train.columns:
                scaler = MinMaxScaler(feature_range=(-1,1))
                s_s = scaler.fit_transform(data_train[j].values.reshape(-1,1))
                s_s=np.reshape(s_s,len(s_s))
                scalers['scaler_'+ j] = scaler
                data_train[j]=s_s
        return scalers, data_train
    
    
    def correlation(self,data, n_columns=0, list_columns=[]):
        """
        Finds the correlation between the selected variables.
        
        :param data: Normalized input data used to find the correlation of each feature.
        :param n_columns: Number of features used in the input data.
        :param list_columns: List of features defined to find their correlation.

        :return correlation_matrix: Dataframe with the correlation between the selected variables.

        """
        if self.normalization:
            scalers, data=self.min_max_scaler(data)
        heatdata=data.corr()  
        correlation_matrix=pd.DataFrame()
        table = str.maketrans(dict.fromkeys("()"))
        if n_columns==0:
            if len(list_columns)==0:
                for col in data.columns:
                    col_heat=heatdata[[col]].sort_values(by=col, ascending=False)
                    correlation_matrix=pd.concat([correlation_matrix,col_heat.reset_index()],axis=1)

                return correlation_matrix
            else:
                for col in list_columns:
                    col_heat=heatdata[[col]].sort_values(by=col, ascending=False)
                    correlation_matrix=pd.concat([correlation_matrix,col_heat.reset_index()],axis=1)
                    correlation_matrix[col]=correlation_matrix[col].round(2)
                    correlation_matrix.columns=["item_id",self.string_normalization(col.translate(table))]

                return correlation_matrix
        else:
            for col in data[0:n_columns].columns:
                col_heat=heatdata[[col]].sort_values(by=col, ascending=False)
                correlation_matrix=pd.concat([correlation_matrix,col_heat.reset_index()],axis=1)
                correlation_matrix[col]=correlation_matrix[col].round(2)
                correlation_matrix.columns=["item_id",self.string_normalization(col.translate(table))]
            return correlation_matrix


    def causality(self, data, outcome, refute=False):
        """
        Finds the causality between the selected variables.
        
        :param data: Normalized input data used to find the causality of each feature.
        :param threshold: Minimum causality value.
        :param max_iter: Number of iterations used to converge the model.

        :return affects: Dataframe with the features that are affected by the column name variable.
        :return Var_affected: Dataframe with the features that affects the column name variable.

        """
        values=[]
        items=[]
        refute_values=[]
        refute_placebo=[]
        refute_subset=[]
        cols=data.columns.tolist()
        cols.remove(outcome)
        for item in cols:
            items=np.append(items, item)
            columns=data.columns.tolist()
            columns.remove(item)
            columns.remove(outcome)
            model=CausalModel(
                data = data,
                treatment=item,
                outcome=outcome,
                common_causes=columns
            )
            #Identify the causal effect
            identified_estimand = model.identify_effect()
            #Estimate the causal effect 
            estimate = model.estimate_effect(identified_estimand, method_name="backdoor.linear_regression", test_significance=True)

            values=np.append(values, estimate.value)
            print(item, ": ", estimate.value)
            if refute:
                refute_results=model.refute_estimate(identified_estimand, estimate, method_name="random_common_cause")
                refute_values=np.append(refute_values, refute_results.new_effect)

                res_placebo=model.refute_estimate(identified_estimand, estimate, method_name="placebo_treatment_refuter", placebo_type="permute")
                refute_placebo=np.append(refute_placebo, res_placebo.new_effect)

                res_subset=model.refute_estimate(identified_estimand, estimate,method_name="data_subset_refuter", subset_fraction=0.5)
                refute_subset=np.append(refute_subset, res_subset.new_effect)
        df=pd.DataFrame(items, columns=["item_id"])
        df["causality"]=values.round(2)
        if refute:
            df["refute"]=refute_values.round(2)
            df["refute_placebo"]=refute_placebo.round(3)
            df["refute_subset"]=refute_subset.round(2)
        df=df.sort_values(by="causality", ascending=False)
        table = str.maketrans(dict.fromkeys("()"))
        df=df.rename(columns={"causality":(self.string_normalization(outcome.translate(table)))})
        return df


