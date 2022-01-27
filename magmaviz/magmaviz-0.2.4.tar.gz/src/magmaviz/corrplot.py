import altair as alt
import pandas as pd

def corrplot(df, print_corr=True, shape="circle"):
    """Generates a correlation plot for the numeric variables
    in a dataframe, and prints the correlation values.

    Parameters
    ----------
    df : DataFrame
        The dataframe containing the data to be plotted.
    print_corr : boolean
        Determines whether the function will print the
        correlation values after the graph or not.
    shape : string
        Determines the shape to use in the graph to represent
        the value of the correlation. Its possible values 
        are "circle" and "square".

    Returns
    -------
    altair.vegalite.v4.api.Chart
        Correlation plot between the numerical variables
        of a dataframe.

    Examples
    --------
    >>> from magmaviz.magmaviz import corrplot
    >>> corrplot(movies_data, print_corr=True, shape="square")
    """

    # Checking that the dataframe is a pandas dataframe type
    if not isinstance(df, pd.core.frame.DataFrame):
        raise TypeError(
            "'df' should be of type 'pandas.core.frame.DataFrame', a pandas dataframe."
        )
    
    # Checking that type for print_corr is a boolean
    if not isinstance(print_corr, bool):
        raise TypeError("'print_corr' should be of type 'boolean'.")
        
    # Checking that type of shape is string
    if not isinstance(shape, str):
        raise TypeError("'shape' should be of type 'str'.")

    # Checking if shape has a valid value
    if shape not in ["circle", "square"]:
        raise ValueError("The value specified for 'shape' is not valid. It should be 'circle' or 'square'")

    # Create the correlation dataframe
    corr_df = (
        df
        .select_dtypes('number')
        .corr('spearman')
        .stack()                            # Get df into long format for altair
        .reset_index(name='Correlation'))   # Name the index that is reset to "Correlation"

    # Set cases where the variable is compared vs itself to zero
    corr_df.loc[corr_df['Correlation'] == 1, 'Correlation'] = 0

    # Add a column with the absolute value
    corr_df['abs'] = corr_df['Correlation'].abs()

    # Rename the columns
    corr_df.rename(columns={'level_0': 'Variable1', 'level_1': 'Variable2'}, inplace=True)
    
    # Creating the plot with circles
    if shape == "circle":
        chart = alt.Chart(corr_df).mark_circle().encode(
                    x='Variable1',
                    y='Variable2',
                    size='abs',
                    color=alt.Color('Correlation', scale=alt.Scale(scheme='purpleorange', domain=(-1, 1))))
    
    # Creating the plot with squares
    if shape == "square":
        chart = alt.Chart(corr_df).mark_square().encode(
                    x='Variable1',
                    y='Variable2',
                    size='abs',
                    color=alt.Color('Correlation', scale=alt.Scale(scheme='purpleorange', domain=(-1, 1))))
    
    # Printing the correlations without repeating the combination of variables
    if print_corr:
        print_corr = corr_df.copy()
        print_corr['Variable12'] = print_corr['Variable1'] + print_corr['Variable2']
        print_corr['Variable21'] = print_corr['Variable2'] + print_corr['Variable1']

        for value in print_corr['Variable21']:
            if value in list(print_corr['Variable12']):
                print_corr.drop(print_corr[print_corr.Variable21 == value].index, inplace=True)

        print_corr.reset_index(drop=True, inplace=True)
        print(print_corr[['Variable1', 'Variable2', 'Correlation']])
    
    return chart