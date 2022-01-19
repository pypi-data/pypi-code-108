def mars_modeling(
    x_train,
    y_train,
    x_test,
    model_weights=[1, 1],
    allow_missing=True,
    max_degree=1,
    max_terms=100,
    max_iter=100,
    model_out="model.joblib"
):

    """
    Create a predictive model using MARS (pyearth). Further documentation on the algorythm can be found at https://contrib.scikit-learn.org/py-earth/
    
    See https://pypi.org/project/gitlabds/ for more information and example calls.
    """

    import pandas as pd
    import copy
    import joblib
    from pyearth import Earth, export
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LogisticRegression, LinearRegression

    pd.set_option("display.float_format", lambda x: "%.10f" % x)

    model = Pipeline([("earth",
                       Earth(feature_importance_type="gcv", 
                             allow_missing=allow_missing, 
                             verbose=1,
                             max_degree=max_degree,
                             max_terms=max_terms,
                            ),
                      ),
                      ("log",
                       LogisticRegression(class_weight={0: model_weights[0], 
                                                        1: model_weights[1]},
                                          verbose=1,
                                          solver="liblinear",
                                          max_iter=max_iter,
                                         ),
                      ),
                     ])
    
    model.fit(x_train, y_train)

    # Export Scoring Equation
    # equation = copy.deepcopy(model)
    # equation.named_steps['earth'].coef_ = equation.named_steps['log'].coef_
    # equation = str(export.export_sympy(equation.named_steps['earth']))
    # print(equation)

    # Second Pass using only variables that hit in the first pass. This makes the scoring easier as not all the columns from training dataset are needed -- just the ones that actually hit in the model
    rerun = pd.DataFrame()
    rerun["vars"] = model.named_steps["earth"].xlabels_
    rerun["imps"] = model.named_steps["earth"].feature_importances_
    rerun = rerun[rerun["imps"] > 0]

    x_train = x_train[rerun["vars"].to_list()]
    x_test = x_test[rerun["vars"].to_list()]

    # Re-initialize the model
    model = Pipeline([("earth",
                       Earth(feature_importance_type="gcv", 
                             allow_missing=allow_missing, 
                             verbose=1,
                             max_degree=max_degree,
                             max_terms=max_terms,
                            ),
                      ),
                      ("log",
                       LogisticRegression(class_weight={0: model_weights[0], 
                                                        1: model_weights[1]},
                                          verbose=1,
                                          solver="liblinear",
                                          max_iter=max_iter,
                                         ),
                      ),
                     ])
    
    model.fit(x_train, y_train)

    equation = copy.deepcopy(model)
    equation.named_steps["earth"].coef_ = equation.named_steps["log"].coef_
    equation = str(export.export_sympy(equation.named_steps["earth"]))
    print("\nModeling Equation:")
    print(equation)

    # Save the joblib model file
    joblib.dump(model, model_out)
    print(f"\njoblib model file saved as '{model_out}'")

    return model, equation, x_train, x_test
