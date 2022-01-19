def split_data(df, train_pct=0.7, dv=None, dv_threshold=0.0, random_state=5435):
    """
    This function will split your data into train and test datasets, separating the outcome from the rest of the file. 
    The resultant datasets will be named x_train,y_train, x_test, and y_test.
    
    See https://pypi.org/project/gitlabds/ for more information and example calls.
    """

    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from imblearn.over_sampling import SMOTENC
    from sklearn.utils import resample

    # Determine positive instances of the outcome percentage
    if dv != None:
        # Split Outcome From Other Fields
        x = df.drop(dv, axis=1).copy(deep=True)
        y = df[dv].copy(deep=True)

        # Split Dataset
        x_train, x_test, y_train, y_test = train_test_split(x, 
                                                            y, 
                                                            train_size=train_pct, 
                                                            test_size=1 - train_pct, 
                                                            random_state=random_state, 
                                                            shuffle=True)

        # Get DV Occurance
        dv_pct = len(df[df[dv] != 0]) / len(df)

        # Up-sample if needed
        if dv_pct < dv_threshold:

            print(f'Outcome variable "{dv}" pct: {dv_pct}. Below the dv_threshold value of {dv_threshold}. Will up-sample with SMOTE-NC...')

            # Get list of binary variables (mostly categorical dummy codes)
            cats = pd.DataFrame(x_train.select_dtypes(include=["number"]).nunique(dropna=False, axis=0))
            cats = np.where(cats[0] == 2, True, False)

            # SMOTENC
            sm = SMOTENC(random_state=random_state,
                         categorical_features=cats,
                         sampling_strategy=dv_threshold / (1 - dv_threshold))
            
            x_train, y_train = sm.fit_resample(x_train, y_train)

            # Assign Model Weights (Non-Instance, Positive Instance)
            model_weights = [1 / ((1 - dv_threshold) / (1 - dv_pct)),
                             1 / (dv_threshold / dv_pct)]

        else:
            model_weights = [1, 1]

    else:
        print("You must enter a DV value")

    return x_train, y_train, x_test, y_test, model_weights
