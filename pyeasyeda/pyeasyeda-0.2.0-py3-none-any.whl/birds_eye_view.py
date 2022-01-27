import numpy as np
import pandas as pd
import seaborn as sns
import warnings
import matplotlib.pyplot as plt

def birds_eye_view(df, n=20, var_list=None):
    """Takes in a pandas.DataFrame object, an optional integer for the histogram bin size, an optional custom variable list, and displays 3 different visualization sets.

    1. Histograms for each numeric variable
    2. A bar chart for each categorical variable
    3. A correlation heatmap of the numeric variables.

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe to create the visualizations
    n : int
        bin size for histograms
    var_list : list
        a specific list of variables to examine, defaults to None

    Returns
    -------
    charts: dict
        A dictionary containing the plot objects created by this function

    Examples
    --------
    >>> birds_eye_view(df, n=30)

    """

    if not (type(df) == pd.DataFrame):
        raise TypeError("df must be input as a DataFrame.")

    if type(var_list) != list and var_list is not None:
        raise TypeError("var_list must be a list.")

    if type(n) != int:
        raise TypeError("n must be an integer.")

    # Generate the visualizations

    viz = {}
    heatmap_list = []
    heatmap = []
    histograms = []
    bar_charts = []

    # Defining the numeric and categorical variables
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = df.select_dtypes(include=("object" or "string")).columns.to_list()

    # Plot all the variables
    if var_list is None:

        # Histograms
        for num_col in numeric:
            chart = sns.histplot(df, x=(num_col), bins=n, kde=True)
            plt.title("Histogram for " + num_col)
            plt.figure()
            histograms.append(chart)

        # Bar Charts
        for cat_col in categorical:
            if len(pd.unique(df[cat_col])) > 11:
                print(cat_col, " has too many unique values")
            else:
                chart = sns.countplot(data=df, x=(cat_col))
                plt.title("Bar Chart for " + cat_col)
                plt.figure()
                bar_charts.append(chart)

        # Heatmap
        corr_matrix = df[numeric].corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=np.bool_))
        chart = sns.heatmap(data=corr_matrix,
                            vmin=-1,
                            vmax=1,
                            annot=True,
                            cmap="BrBG",
                            mask=mask
        )
        plt.title("Heatmap of correlation between numeric features")
        plt.figure(figsize=(12, 6))
        print(chart)
        viz["heatmap"] = chart

    # Plot just the custom variables from var_list (if applicable)
    else:
        
        for custom_col in var_list:
            all_cols = df.columns.to_list()
            if custom_col not in all_cols:
                raise TypeError("Variable name " +
                                custom_col +
                                " not found in data frame, please check inputs in var_list.")

            # Histograms
            if custom_col in numeric:
                heatmap_list.append(custom_col)
                chart = sns.histplot(df, x=(custom_col), bins=n, kde=True)
                plt.title("Histogram for " + custom_col)
                plt.figure()
                histograms.append(chart)

            # Bar Charts
            elif custom_col in categorical:
                if len(pd.unique(df[custom_col])) > 11:
                    print(custom_col, " has too many unique values")
                else:
                    chart = sns.countplot(data=df, x=(custom_col))
                    plt.title("Bar Chart for " + custom_col)
                    plt.figure()
                    bar_charts.append(chart)

        # Heatmap
        corr_matrix = df[heatmap_list].corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=np.bool_))
        chart = sns.heatmap(data=corr_matrix,
                            vmin=-1,
                            vmax=1,
                            annot=True,
                            cmap="BrBG",
                            mask=mask
        )
        plt.title("Heatmap of correlation between numeric features")
        plt.figure(figsize=(12, 6))
        viz["heatmap"] = chart

    viz["histograms"] = histograms
    viz["bar_charts"] = bar_charts
    
    return viz