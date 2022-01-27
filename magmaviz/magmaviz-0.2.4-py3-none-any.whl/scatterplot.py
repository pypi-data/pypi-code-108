import altair as alt
import pandas as pd
import re
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

def scatterplot(df, x, y, c="", t="", o=0.5, s=50, xtitle="", ytitle="", ctitle="", xzero=False, yzero=False, shapes=True):
    """Plot a scatterplot on the dataframe with the magma color scheme.
    
    Parameters
    ----------
    df : dataframe
         Dataframe containing the numerical features x and y
    x : string
        Column-name of the numerical variable to be plotted on the x-axis
    y : string
        Column-name of the numerical variable to be plotted on the y-axis
    c : string
        Column-name of the categorical variable to color-code the data points
        Default value is blank for cases when there is no categorical column
    t : string
        Title of the plot. Default value is blank. If not provided,
        title will be computed based on x, y and/or c
    o : float
        Opacity of the data points
        Default value is 0.5
    s : integer
        Size of the data points
        Default value is 50
    xtitle : string
             Title of the x-axis. Default value is blank. If not provided,
             title will be proper case of the x axis column
    ytitle : string
             Title of the y-axis. Default value is blank. If not provided,
             title will be proper case of the y axis column
    ctitle : string
             Title of the color legend. Default value is blank. If not provided,
             title will be proper case of the color column
    xzero : boolean
            Scale the x-axis to start from 0 by specifying True
            Default value is set to False
    yzero : boolean
            Scale the y-axis to start from 0 by specifying True
            Default value is set to False
    shapes : boolean
             Assign the color column to the shape attribute of the plot if True
             Default value is set to True

    Returns
    -------
    altair.vegalite.v4.api.Chart
        Scatterplot between the numerical variables x and y

    Example
    -------
    >>> from magmaviz.scatterplot import scatterplot
    >>> from vega_datasets import data
    >>> scatterplot(data.iris(), "sepalLength", "sepalWidth", "species",
                    "Iris Sepal Length vs Sepal Width across Species",
                    1.0, 50, "Sepal Length", "Sepal Width", "", False, False, True)
    """

    # Basic checks to see if parameters passed to function call contain expected values
    # check if the dataframe is a pandas dataframe
    if not isinstance(df, pd.core.frame.DataFrame):
        raise TypeError("'df' should be of type 'pandas.core.frame.DataFrame', a pandas dataframe.")

    # check if column name for x-axis is a string
    if not isinstance(x, str):
        raise TypeError("Invalid value passed to 'x' axis: Assign column name as a 'string'.")

    # check if column name for y-axis is a string
    if not isinstance(y, str):
        raise TypeError("Invalid value passed to 'y' axis: Assign column name as a 'string'.")

    # check if column name for color is a string
    if not isinstance(c, str):
        raise TypeError("Invalid value passed to 'color' variable: Assign column name as a 'string'.")

    # check if title is a string
    if not isinstance(t, str):
        raise TypeError("Invalid value passed to 't' variable: Assign title as a 'string'.")

    # check if opacity is a number
    if not isinstance(o, float):
        raise TypeError("Invalid value passed to 'o' variable: Assign opacity value as a decimal between 0 and 1.")

    # check if size is an integer
    if not isinstance(s, int):
        raise TypeError("Invalid value passed to 's' variable: Assign size value as an integer between 1 and 100.")

    # check if x-axis title is a string
    if not isinstance(xtitle, str):
        raise TypeError("Invalid value passed to 'xtitle' variable: Assign x-axis title as a 'string'.")

    # check if y-axis title is a string
    if not isinstance(ytitle, str):
        raise TypeError("Invalid value passed to 'ytitle' variable: Assign y-axis title as a 'string'.")

    # check if color legend title is a string
    if not isinstance(ctitle, str):
        raise TypeError("Invalid value passed to 'ctitle' variable: Assign color legend title as a 'string'.")

    # check if xzero is a boolean
    if not isinstance(xzero, bool):
        raise TypeError("Invalid value passed to 'xzero' variable: Assign boolean True to begin x axis from zero.")

    # check if yzero is a boolean
    if not isinstance(yzero, bool):
        raise TypeError("Invalid value passed to 'ctitle' variable: Assign boolean True to begin y axis from zero.")

    # check if shapes is a boolean
    if not isinstance(shapes, bool):
        raise TypeError("Invalid value passed to 'shapes' variable: Assign boolean True to show different shapes for each color category.")

    # Advanced checks to see whether columns exists, opacity and size are within expected range, etc.
    # check if column name assigned to x-axis is present in the dataframe
    assert x in list(
        df.columns
    ), "The column specified for 'x' axis does not exist in the dataframe."

    # check if column name assigned to y-axis is present in the dataframe
    assert y in list(
        df.columns
    ), "The column specified for 'y' axis does not exist in the dataframe."

    # check if column name assigned to color is present in the dataframe
    if c != "":
        assert c in list(
            df.columns
        ), "The column specified for 'color' does not exist in the dataframe."

    # check if opacity value is in the range 0.1 to 1.0
    if o < 0.1 or o > 1.0:
        raise TypeError("Opacity value must be in the range [0.1, 1.0]")

    # check if size value is in the range 1 to 100
    if s < 1 or s > 100:
        raise TypeError("Size of data points must be in the range [1, 100]")

    # check if x-axis column is numeric or not
    assert is_numeric_dtype(df[x]), "The column assigned to 'x' axis is not of type numeric."

    # check if y-axis column is numeric or not
    assert is_numeric_dtype(df[y]), "The column assigned to 'y' axis is not of type numeric."

    # check if color column is string or not
    if c != "":
        assert is_string_dtype(df[c]), "The column assigned to 'color' is not of type string."

    # add proper titles to axes, legend and plot
    if xtitle == "":
        xtitle = re.sub(r"[_.,-]", " ", x)
    if ytitle == "":
        ytitle = re.sub(r"[_.,-]", " ", y)
    if ctitle == "":
        ctitle = re.sub(r"[_.,-]", " ", c)
    if t == "":
        if c == "":
            t = f"{xtitle.title()} vs {ytitle.title()}"
        else:
            t = f"{xtitle.title()} vs {ytitle.title()} by {ctitle.title()}"

    # scatterplot
    if c == "":
        plot = alt.Chart(
            data=df, title=t
        ).mark_point(
            opacity=o, size=s, color="#721F81"
        ).encode(
            alt.X(x, title=xtitle.capitalize(), scale=alt.Scale(zero=xzero)),
            alt.Y(y, title=ytitle.capitalize(), scale=alt.Scale(zero=yzero))
        )
    else:
        if shapes is False:
            plot = alt.Chart(
                data=df, title=t
            ).mark_point(
                opacity=o, size=s
            ).encode(
                alt.X(x, title=xtitle.capitalize(), scale=alt.Scale(zero=xzero)),
                alt.Y(y, title=ytitle.capitalize(), scale=alt.Scale(zero=yzero)),
                alt.Color(c, title=ctitle.capitalize(), scale=alt.Scale(scheme="magma"))
            )
        else:
            plot = alt.Chart(
                data=df, title=t
            ).mark_point(
                opacity=o, size=s
            ).encode(
                alt.X(x, title=xtitle.capitalize(), scale=alt.Scale(zero=xzero)),
                alt.Y(y, title=ytitle.capitalize(), scale=alt.Scale(zero=yzero)),
                alt.Color(c, title=ctitle.capitalize(), scale=alt.Scale(scheme="magma")),
                shape=c
            )

    return plot