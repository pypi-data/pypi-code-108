from skopt.space import Real, Integer, Categorical


class BayesParamas:

    DecisionTreeParams = {
        "estimator__criterion": Categorical(["gini", "entropy"]),
        "estimator__max_depth": Integer(3, 15)
    }
    KNeighborsParams = {
        "estimator__n_neighbors": Integer(1, 40),
        "estimator__weights": Categorical(["uniform", "distance"]),
        "estimator__p": Integer(1, 2)
    }
    LogisticRegressionParams = {
        "estimator__fit_intercept": Categorical([True, False]),
        "estimator__C": Real(0.001, 1000, prior="log-uniform")
    }
    SVCParams = {
        "estimator__gamma": Real(0.001, 1000, prior='log-uniform'),
        "estimator__C": Real(0.001, 1000, prior='log-uniform'),
        "estimator__kernel": Categorical(["rbf", "poly", "sigmoid"])
    }
    RandomForestParams = {
        "estimator__n_estimators": Integer(100, 200),
        "estimator__max_depth": Integer(20, 80),
        "estimator__max_features": Real(0.1, 0.8, prior="log-uniform"),
        "estimator__min_samples_leaf": Integer(1, 20)
    }
    AdaBoostParams = {
        "estimator__n_estimators": Integer(10, 500),
        "estimator__learning_rate": Real(0.0001, 0.1, prior="log-uniform")
    }

    XGBParams = {
        "estimator__max_depth": Integer(3, 10),
        "estimator__colsample_bytree": Real(0.1, 1, prior="log-uniform"),
        "estimator__n_estimators": Integer(100, 200),
        "estimator__subsample": Real(0.1, 1, prior="log-uniform"),
        "estimator__gamma": Integer(1, 10),
        "estimator__learning_rate": [0.01, 0.1, 1],
        "estimator__reg_alpha": Real(0.01, 10, prior="log-uniform"),
        "estimator__reg_lambda": Real(0.01, 10, prior="log-uniform")
    }

    LGBMParams = {
        "estimator__num_leaves": Integer(10, 20),
        "estimator__min_child_samples": Integer(100, 300),
        "estimator__min_child_weight": Real(1e-5, 1e+4, prior="log-uniform"),
        "estimator__subsample": Real(0.2, 0.9, prior="log-uniform"),
        "estimator__colsample_bytree": Real(0.2, 0.9, prior="log-uniform"),
        "estimator__reg_alpha": Real(0, 50, prior="log-uniform"),
        "estimator__reg_lambda": Real(0, 50, prior="log-uniform"),
    }

    CatBoostParams = {
        "estimator__depth": Integer(4, 8),
        "estimator__iterations": [500, 1000],
        "estimator__learning_rate": [0.001, 0.01, 0.1],
        "estimator__l2_leaf_reg": Integer(3, 100),
        "estimator__border_count": Integer(10, 200)
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
