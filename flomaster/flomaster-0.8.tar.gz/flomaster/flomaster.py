from .helpers import * 
from .plots import *
from .col_type_detector import *
import warnings

ONE_NUMERIC = ['Histogram', 'Distplot']
ONE_CATEOGIRCAL = ['Donut', 'Pie', 'Histogram']
ONE_TEXT = ['Wordcloud']
TWO_NUMERIC = ["Scatter", "Scatter plot with margins", "2D density plot", "Distplot", "Histogram", "Basic Stats"]
TWO_NUMERIC_SORTED = ['Connected Scatter', "Area plot", "Line plot"]
ONE_CATEOGIRCAL_ONE_NUMERICAL = ['Box', "Violin", "Basic Stats"]
TWO_CATEGORICAL = ['Cross tab', "Stacked bar"]
ONE_DATETIME_ONE_NUMERIC = ['Connected Scatter']




def generate_flomaster_plot(df, x="None", y=[], group_by=None, plot_type=None, x_axis=None, y_axis=None, title=None):
    """
    Function generates interactiv plot for given dataframe and columns

    Args:
        df (pd.DataFrame)
        x (str): name of the column to use as x_axis
        y (str or list): either one column or list of columns to plot at y axis
        group_by (str): column by which to group data (default is None)
        plot_type (str): possible values vary depending on input data, the list is`            
            ONE_NUMERIC = ['Histogram', 'Distplot']
            ONE_CATEOGIRCAL = ['Donut', 'Pie', 'Histogram']
            ONE_TEXT = ['Wordcloud']
            TWO_NUMERIC = ["Scatter", "Scatter plot with margins", "2D density plot", "Distplot", "Histogram", "Basic Stats"]
            TWO_NUMERIC_SORTED = ['Connected Scatter', "Area plot", "Line plot"]
            ONE_CATEOGIRCAL_ONE_NUMERICAL = ['Box', "Violin", "Basic Stats"]
            TWO_CATEGORICAL = ['Cross tab', "Stacked bar"]
            ONE_DATETIME_ONE_NUMERIC = ['Connected Scatter']   
        x_axis (str): defaults to x columns name
        y_axis (str): defaults to y, if y is a list then to first element of y
        title (str): defaults to f"{x_axis} vs {y_axis}"
    
    Note:
        Some illogical results might occur in case when column_type_detector classifies some
        column incorrectly, also note that this package is in a very early stage of development

    Raises:
        ValueError: if plot_type is not from allowed list
    
    Returns:
        plotly figure object
    """
    if type(y) == str:
        y = [y]

    data_types = get_column_types(df, num_unique_categories=2)

    if x_axis is None:
        x_axis = x
    if y != [] and y_axis is None:
        y_axis = y[0]
    if title is None:
        title = f"{x_axis} vs {y_axis}"
    

    x_dtype = get_data_type_for_given_feature(data_types, x)
    y_dtype = get_data_type_for_given_feature(data_types, y[0])

    # print(x)
    # print(y)
    # print(x_dtype)
    # print(y_dtype)

    # one feature
    if x != "None" and y[0] == 'None':
        if x_dtype == 'numeric': # 1
            possible_graphs = ONE_NUMERIC

            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")
            else:
                fig = one_numeric(df, x, group_by, plot_type)
                add_labels_to_fig(fig, x_axis, y_axis, title)
                return fig

        if x_dtype == 'categorical': # 2
            possible_graphs = ONE_CATEOGIRCAL
            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")

            else:
                fig = one_categoric(df, x, group_by, plot_type)
                add_labels_to_fig(fig, x_axis, y_axis, title)        
                return fig

        if x_dtype == 'texts': # 3
            possible_graphs = ONE_TEXT

            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")
            else:
                fig = one_textual(df, x)
                return fig


    # two features
    if x != "None" and y[0] != 'None':
        # two numeric
        if x_dtype == "numeric" and y_dtype == 'numeric': # 4
            global TWO_NUMERIC
            if df[x].to_list() == sorted(df[x].to_list()):
                TWO_NUMERIC += TWO_NUMERIC_SORTED
            
            possible_graphs = TWO_NUMERIC 

            if len(df)>2000 and plot_type in ["Histogram", "Scatter"]:
                warnings.warn('**Data has two many rows, we suggest plotting \
                    with one on the folowing: "Scatter plot with margins", "2D density plot", "Distplot"**')
            
            if len(df)<2000 and plot_type not in ["Histogram", "Scatter", "Basic Stats"]:
                warnings.warn('**Data has two little rows, we suggest plotting \
                    with one on the folowing: "Histogram", "Scatter"**')

                    
            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")
            else:
            
                fig = two_numeric(df, x, y[0], group_by, plot_type)
                add_labels_to_fig(fig, x_axis, y_axis, title)        
                return fig         

        #one numeric one categoric # 5
        if x_dtype == "categorical" and y_dtype == 'numeric':
            possible_graphs = ONE_CATEOGIRCAL_ONE_NUMERICAL

            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")
            else:
                fig = one_numeric_one_categorical(df, x, y, group_by, plot_type)
                add_labels_to_fig(fig, x_axis, y_axis, title)        
                return fig         
                
        # two categoricals
        if x_dtype == "categorical" and y_dtype == 'categorical':
            possible_graphs = TWO_CATEGORICAL

            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")
            else:
                if plot_type == 'Cross tab':
                    fig = two_categorical(df, x, y[0], plot_type)
                    
                if plot_type == 'Stacked bar':
                    fig = two_categorical(df, x, y[0], plot_type)
                    add_labels_to_fig(fig, x_axis, y_axis, title)   
                return fig         
                    
        # one datetime one numeric
        if x_dtype == "datetime" and y_dtype == 'numeric':
            global ONE_DATETIME_ONE_NUMERIC
            if check_list_in_list(list(df.columns), ['Date', "Open", "High", "Low", "Close"]):
                ONE_DATETIME_ONE_NUMERIC += ["Stock price"]
            possible_graphs = ONE_DATETIME_ONE_NUMERIC

            if (plot_type is not None) and (plot_type not in possible_graphs):
                raise ValueError(f"Please select one from {possible_graphs}")
            else:
                fig = one_datetime_one_numeric(df, x, y, group_by,plot_type)
                add_labels_to_fig(fig, x_axis, y_axis, title)        
                return fig
    
    return f"Something went wrong, contac team Flomaster"
     