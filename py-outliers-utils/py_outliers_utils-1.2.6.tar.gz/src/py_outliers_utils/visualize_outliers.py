import pandas as pd
import altair as alt

def visualize_outliers(dataframe, columns=None, type='violin'):
    """
    A function that plot the distribution of the given data.
    
    Parameters
    ----------
    dataframe : pandas.core.frame.DataFrame
        The target dataframe where the function is performed.
    
    columns : list, default=None
        The target columns where the function needed to be performed. Default is None, the function will check all columns.
    
    type : string, default='violin'
        The method of plotting the distribution.
        - if "violin" : Return a violin plot with boxplot layer
        - if "boxplot" : Return a boxplot


    Returns
    -------
    altair.vegalite.v4.api.Chart
        an altair plot with data distribution.
    
    Examples
    --------
    >>> import pandas as pd
    >>> import altair as alt
        
    >>> df = pd.DataFrame({
    >>>    'SepalLengthCm' : [0.1, 4.9, 52.7, 5.5, 5.1, 50, 5.4, 179.0, 5.2, 5.3, 5.1],
    >>>    'SepalWidthCm' : [1.4, 1.4, 20, 2.0, 0.7, 1.6, 1.2, 14, 1.8, 1.5, 2.1],
    >>>    'PetalWidthCm' : [0.2, 0.2, 0.2, 0.3, 0.4, 0.5, 0.5, 0.6, 0.4, 0.2, 5]
    >>> })

    >>> visualize_outliers(df, columns=['SepalLengthCm', 'SepalWidthCm'])
    """

    ## Handle dataframe type error (Check if dataframe is of type Pandas DataFrame)
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"passed dataframe is of type {type(dataframe).__name__}, should be DataFrame")
        
    ## Handle empty dataframe or dataframe with all NAN
    if dataframe.empty or dataframe.dropna().empty:
        raise ValueError("passed dataframe is None")
    
    ## Handle columns type error (Check if columns are None or type list)
    if not columns is None and not isinstance(columns, list):
        raise TypeError(f"passed columns is of type {type(columns).__name__}, should be list or NoneType")
    
    ## Handle type Value error (Check if type has value 'violin' or 'boxplot')
    if type!='violin' and type!='boxplot':
        raise ValueError("passed type should have value 'violin' or 'boxplot'")
    
    ## Select given columns
    if columns is None:
        df = dataframe
    else:
        df = dataframe[columns]
    
    ## Select numeric columns
    dfnumeric = df._get_numeric_data() 
    
    ## Melt dataframe for plot
    dfmelt = dfnumeric.melt()  
    
    ## Plot according type
    if type == 'violin':
        
        ## The boxplot layer
        boxplot = alt.Chart().mark_boxplot(color='black').encode(
                            alt.Y('value')
                    ).properties(width=100)
        
        ## The violinplot layer
        violin = alt.Chart().transform_density(
                'value',
                as_=['value', 'density'],
                groupby=['variable']
            ).mark_area(orient='horizontal').encode(
                y=alt.Y('value'),
                color=alt.Color('variable:N', legend=None),
                x=alt.X(
                    'density:Q',
                    stack='center',
                    impute=None,
                    title=None,
                    scale=alt.Scale(nice=False,zero=False),
                    axis=alt.Axis(labels=False, values=[0], grid=False, ticks=True),
                ),
            )
        
        ## Overlay two layers
        violinbox = alt.layer(violin, boxplot, data=dfmelt).facet('variable:N', columns=5).resolve_scale(x=alt.ResolveMode("independent"))
        return violinbox
    
    else:
        boxplot = alt.Chart(dfmelt).mark_boxplot().encode(
                    alt.X(title = None),
                    alt.Y("value"),
                    alt.Color("variable", legend = None) 
                ).properties(
                    width=100
                ).facet('variable:N', columns=4)
        return boxplot
