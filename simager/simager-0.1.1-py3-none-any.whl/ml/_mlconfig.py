from dataclasses import MISSING, dataclass, field
from typing import List, Optional


@dataclass
class ConfigData:
    """Data Configuration

    Args:
        target (str, required): Name of the target column

        cat_features (list, required): Column names of the categorical fields. Defaults to []

        num_features (list, required): Column names of the numerical fields. Defaults to []

        test_size (float, optional): Number of test size when spliting the data. Defaults to 0.2

        random_state (int, optional): The random state that you provide is used as a seed to the random number generator. Defaults to 42

    """
    target: str = field(
        default=MISSING
    )
    cat_features: List = field(
        default_factory=[]
    )
    num_features: List = field(
        default_factory=[]
    )
    test_size: Optional[float] = field(
        default=0.2
    )
    random_state: Optional[int] = field(
        default=42
    )


@dataclass
class ConfigPreprocess:
    """Data Preprocessing Configuration

    Args:
        cat_imputer (str, optional): Imputation method for categorical fields. Defaults to None
            you can only provide: `None` `SimpleImputer` method

        num_imputer (str, optional): Imputation method for numerical fields. Defaults to None
            you can choose: `None` `SimpleImputer` `KNNImputer`method

        scaler (str, optional): Standardize a dataset along any axis. Defaults to None
            you can choose: `None` `StandardScaler` `MinMaxScaler` `RobustScaler` `QuantileTransformer` `PowerTransformer` `Normalizer`

        encoder (str, optional): Encoder method for categorical fields. Defaults to None
            you can choose: `None` `OrdinalEncoder` `OneHotEncoder`

        resample (str, optional): resampling method for handling unbalance data. Defaults to None
            you can choose: `None` `oversampling` by SMOTE `undersampling` by AllKNN

    """
    cat_imputer: Optional[str] = field(
        default=None
    )
    num_imputer: Optional[str] = field(
        default=None
    )
    scaler: Optional[str] = field(
        default=None
    )
    encoder: Optional[str] = field(
        default=None
    )
    resample: Optional[str] = field(
        default=None
    )

    def __setattr__(self, name, value):
        if name == "cat_imputer":
            # https://scikit-learn.org/stable/modules/impute.html
            ls = [
                None,
                "SimpleImputer"
            ]
            assert value in ls, f"value of {name} should be: {ls}"
            self.__dict__[name] = value
        if name == "num_imputer":
            # https://scikit-learn.org/stable/modules/impute.html
            ls = [
                None,
                "SimpleImputer",
                "KNNImputer"
            ]
            assert value in ls, f"value of {name} should be: {ls}"
            self.__dict__[name] = value
        elif name == "scaler":
            # https://scikit-learn.org/stable/modules/preprocessing.html#normalization
            ls = [
                None,
                "StandardScaler",
                "MinMaxScaler",
                "RobustScaler",
                "QuantileTransformer",
                "PowerTransformer",
                "Normalizer"
            ]
            assert value in ls, f"value of {name} should be: {ls}"
            self.__dict__[name] = value
        elif name == "encoder":
            # https://scikit-learn.org/stable/modules/preprocessing.html#normalization
            ls = [
                None,
                "OrdinalEncoder",
                "OneHotEncoder"
            ]
            assert value in ls, f"value of {name} should be: {ls}"
            self.__dict__[name] = value
        elif name == "resample":
            # https://scikit-learn.org/stable/modules/preprocessing.html#normalization
            ls = [
                None,
                "oversampling",
                "undersampling"
            ]
            assert value in ls, f"value of {name} should be: {ls}"
            self.__dict__[name] = value


class Algo:
    algorithm = [
        "DecisionTreeClassifier",
        "KNeighborsClassifier",
        "LogisticRegression",
        "SVC",
        "RandomForestClassifier",
        "AdaBoostClassifier",
        "XGBClassifier",
        "LGBMClassifier",
        "CatBoostClassifier",
    ]


@dataclass
class ConfigModel:
    """Model Configuration

    Args:
        algorithm (list, optional): Machine learning algorithm that you want to compare.
        If not provide, this will be execute all algorithm
            Available algorithms:
                DecisionTreeClassifier
                KNeighborsClassifier
                LogisticRegression
                SVC
                RandomForestClassifier
                AdaBoostClassifier
                XGBClassifier
                LGBMClassifier
                CatBoostClassifier

        metrics (str, optional): Evaluation metrics from the models. Default to `accuracy`
            you can choose:
                accuracy
                precision
                recall
                f1

    """
    algorithm: Optional[List] = field(
        default_factory=lambda: Algo.algorithm
    )
    metrics: Optional[str] = field(
        default="accuracy"
    )

    def __setattr__(self, name, value):
        if name == "algorithm":
            for i in value:
                assert i in Algo.algorithm, f"value of {i} should be one of: {Algo.algorithm}"
            self.__dict__[name] = value
        elif name == "metrics":
            ls = [
                "accuracy",
                "precision",
                "recall",
                "f1"
            ]
            assert value in ls, f"value of {name} should be: {ls}"
            self.__dict__[name] = value
