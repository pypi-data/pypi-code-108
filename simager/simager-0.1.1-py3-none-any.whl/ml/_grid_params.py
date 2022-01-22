import numpy as np
from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_uniform


class GridParamas:

    DecisionTreeParams = {
        "estimator__criterion": ["gini", "entropy"],
        "estimator__max_depth": np.arange(3, 15)
    }
    KNeighborsParams = {
        "estimator__n_neighbors": np.arange(1, 31, 2),
        "estimator__weights": ["uniform", "distance"],
        "estimator__p": [1, 1.5, 2]
    }
    LogisticRegressionParams = {
        "estimator__fit_intercept": [True, False],
        "estimator__C": np.logspace(-3, 3, 7)
    }

    SVCParams = {
        "estimator__gamma": ["scale", "auto", 1.e-03, 1.e-02, 1.e-01, 1.e+00, 1.e+01, 1.e+02, 1.e+03],
        "estimator__C": [1.e-03, 1.e-02, 1.e-01, 1.e+00, 1.e+01, 1.e+02, 1.e+03],
        "estimator__kernel": ["linear", "rbf", "poly", "sigmoid"]
    }
    RandomForestParams = {
        "estimator__n_estimators": [100, 150, 200],
        "estimator__max_depth": [20, 50, 80],
        "estimator__max_features": [0.3, 0.6, 0.8],
        "estimator__min_samples_leaf": [1, 5, 10]
    }
    AdaBoostParams = {
        "estimator__n_estimators": [10, 50, 250, 500],
        "estimator__learning_rate": [0.0001, 0.001, 0.01, 0.1]
    }

    XGBParams = {
        "estimator__max_depth": [3, 6, 10],
        "estimator__colsample_bytree": [0.4, 0.6, 0.8],
        "estimator__n_estimators": [100, 150, 200],
        "estimator__subsample": [0.4, 0.6, 0.8],
        "estimator__gamma": [1, 5, 10],
        "estimator__learning_rate": [0.01, 0.1, 1],
        "estimator__reg_alpha": [0.01, 0.1, 10],
        "estimator__reg_lambda": [0.01, 0.1, 10]
    }

    LGBMParams = {"estimator__num_leaves": sp_randint(6, 50).rvs(9),
                  "estimator__min_child_samples": sp_randint(100, 500).rvs(9),
                  "estimator__min_child_weight": [1e-5, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4],
                  "estimator__subsample": sp_uniform(loc=0.2, scale=0.8).rvs(9),
                  "estimator__colsample_bytree": sp_uniform(loc=0.4, scale=0.6).rvs(9),
                  "estimator__reg_alpha": [0, 1e-1, 1, 2, 5, 7, 10, 50, 100],
                  "estimator__reg_lambda": [0, 1e-1, 1, 5, 10, 20, 50, 100]}

    CatBoostParams = {
        "estimator__depth": [4, 5, 6],
        "estimator__iterations": [500, 1000],
        "estimator__learning_rate": [0.001, 0.01, 0.1],
        "estimator__l2_leaf_reg": [3, 5, 100],
        "estimator__border_count": [10, 50, 200]
    }
    AllParams = {
        "DecisionTreeClassifier": DecisionTreeParams,
        "KNeighborsClassifier": KNeighborsParams,
        "LogisticRegression": LogisticRegressionParams,
        "SVC": SVCParams,
        "RandomForestClassifier": RandomForestParams,
        "AdaBoostClassifier": AdaBoostParams,
        "XGBClassifier": XGBParams,
        "LGBMClassifier": LGBMParams,
        "CatBoostClassifier": CatBoostParams
    }
