import pandas as pd
import numpy as np
import altair as alt


def close_up(df, n=1):
    """Accepts a dataframe and the number of pairs of variables with strongest correlations, and
    returns vertically combined scatterplots with a correlation trend for each pair. 

        Parameters
        ----------
        df : pd.core.frame.DataFrame
             dataframe to create the visualization(s)
        n : int
            number of pairs of variables with strongest correlations to be displayed,
            defaults to 1
            
        Returns
        -------
        chart: altair.vegalite.v4.api.Chart (if n = 1)
               altair.vegalite.v4.api.VConcatChart (if n > 1)
               Vertically combined scatterplots with a correlation trend for each pair

        Examples
        --------
        >>> close_up(df, n = 4)
    """

    # check if input is a DataFrame
    if not isinstance(df, pd.core.frame.DataFrame):
        raise TypeError("df should be of type 'pandas.core.frame.DataFrame'")

    if not isinstance(n, int):
        raise TypeError("n should be of type 'int'.")

    # calculate max allowable integer
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    corr_matrix = df[numeric].corr()
    N_max = len(corr_matrix) * (len(corr_matrix) - 1) / 2

    # check if input exceeds max allowable integer
    if n > N_max:
        raise ValueError("n exceeds total number of coefficients.")

    # initialization
    corr = corr_matrix.to_numpy()
    corr = abs(corr)
    corr = np.triu(corr)  # take only upper triangle
    np.fill_diagonal(corr, 0)  # zero diagonal
    max_row = np.argmax(np.max(corr, axis=1))
    max_col = np.argmax(np.max(corr, axis=0))
    viz = {}  # viz dict to be returned

    # plot
    for i in range(n):
        max_row = np.argmax(np.max(corr, axis=1))
        max_col = np.argmax(np.max(corr, axis=0))
        coef = corr_matrix.iloc[max_row, max_col]
        points = (
            alt.Chart(df, title=f'coeff: {coef:.3f}')
            .mark_point(opacity=0.3)
            .encode(
                alt.X(corr_matrix.columns[max_row]), alt.Y(
                    corr_matrix.columns[max_col])
            )
        )
        viz[i+1] = points + points.transform_regression(
            corr_matrix.columns[max_row], corr_matrix.columns[max_col]).mark_line(size=3)
        corr[max_row, max_col] = 0

    # generate one big chart
    chart = viz[1]
    for i in range(n-1):
        chart &= viz[i+2]

    return chart
