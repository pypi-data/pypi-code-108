from imblearn.under_sampling import AllKNN
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler, RobustScaler, StandardScaler, Normalizer, PowerTransformer, QuantileTransformer
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer


class PipelineGenerator(object):
    def __init__(self,
                 data_config,
                 preprocess_config
                 ):
        self.dc = data_config
        self.pc = preprocess_config
        self._maps_pc = {
            "cat_imputer": {
                "SimpleImputer": SimpleImputer(strategy="most_frequent")
            },
            "num_imputer": {
                "SimpleImputer": SimpleImputer(strategy="mean"),
                "KNNImputer": KNNImputer()
            },
            "scaler": {
                "StandardScaler": StandardScaler(),
                "MinMaxScaler": MinMaxScaler(),
                "RobustScaler": RobustScaler(),
                "QuantileTransformer": QuantileTransformer(),
                "PowerTransformer": PowerTransformer(method='box-cox'),
                "Normalizer": Normalizer()
            },
            "encoder": {
                "OrdinalEncoder": OrdinalEncoder(),
                "OneHotEncoder": OneHotEncoder(handle_unknown="ignore")
            },
            "resample": {
                "oversampling": SMOTE(),
                "undersampling": AllKNN()
            }
        }

    def preprocess_pipe(self):
        cat_pipe = []
        num_pipe = []
        preprocess = None
        if self.pc.cat_imputer:
            cat_pipe.append(("imputer", self._maps_pc["cat_imputer"][self.pc.cat_imputer]))

        if self.pc.num_imputer:
            num_pipe.append(("imputer", self._maps_pc["num_imputer"][self.pc.num_imputer]))

        if self.pc.scaler:
            num_pipe.append(("scaler", self._maps_pc["scaler"][self.pc.scaler]))

        if self.pc.encoder:
            cat_pipe.append(("encoder", self._maps_pc["encoder"][self.pc.encoder]))

        pre = []
        if len(cat_pipe) > 0:
            pre.append(("cat", Pipeline(cat_pipe), self.dc.cat_features))
        if len(num_pipe) > 0:
            pre.append(("num", Pipeline(num_pipe), self.dc.num_features))

        if len(pre) > 0:
            preprocess = ColumnTransformer(pre)

        return preprocess

    def generate_pipe(self):
        pipelines = []
        preprocess = self.preprocess_pipe()
        if preprocess:
            pipelines.append(("preprocess", preprocess))
        if self.pc.resample:
            pipelines.append(("resample", self._maps_pc["resample"][self.pc.resample]))
        return pipelines
