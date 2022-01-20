import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
from wordcloud import WordCloud

import pandas as pd


def one_numeric(df, col_name, group_by=None, plot_type="Histogram"):
    """
        ['Histogram', 'Distplot']
    """
    if plot_type is None:
        plot_type = "Histogram"
    if plot_type=='Histogram': # 1
        fig = px.histogram(df, x=col_name, color=group_by) 
        fig.update_layout(bargap=0.2)
    if plot_type=='Distplot': # 2 groups-y chexav
        fig = ff.create_distplot([df[col_name]], group_labels=['distplot'])
    return fig

def two_numeric(df, x, y, group_by=None, plot_type='Scatter'):
    """
        ["Scatter", "Scatter plot with margins", "2D density plot", "Distplot", "Histogram", "Basic Stats"]
        ["Line plot", 'Connected Scatter', "Area plot"]

    """
    if plot_type is None:
        plot_type = "Scatter"

    x1 = df[x]
    x2 = df[y]


    if plot_type=='Scatter': # 3
        fig = px.scatter(df, x, y, color=group_by)
    
    if plot_type=='Scatter plot with margins': # 4
        fig = px.scatter(df, x, y, marginal_x="histogram", marginal_y="histogram", color=group_by)

    if plot_type=='2D density plot': # 5 color by group chka

        fig = ff.create_2d_density(x1.to_list(), x2.to_list(), point_size=3)#, colorscale=colorscale,
                                #hist_color='rgb(255, 237, 222)', )
    
    if plot_type=='Distplot': # 6 color by group chka
        group_labels = [x,y]
        colors = ['slategray', 'magenta']
        fig = ff.create_distplot([x1, x2], group_labels, bin_size=.5,
                                curve_type='normal',colors=colors)
        fig.update_layout(title_text='Distplot with Normal Distribution')

    if plot_type=='Histogram': # 7 spasel
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=x1,name=x))
        fig.update_layout(bargap=0.2)
        fig.add_trace(go.Histogram(x=x2, name=y))
        fig.update_layout(barmode='overlay')
        fig.update_traces(opacity=0.75)
        fig.update_layout(bargap=0.2)

    if plot_type=="Basic Stats": # 8
        df_for_fig = df[[x]+[y]].describe().loc[["mean", "50%", 'min', 'max']].T
        df_for_fig.rename(columns={'50%':"median"}, inplace=True)
        fig = px.bar(df_for_fig, barmode='group')
            
    if plot_type=='Line plot': # 9 
        fig = px.line(df, x, y, color=group_by)

    if plot_type=='Connected Scatter': # 10
        fig = px.line(df, x, y, markers=True, color=group_by)

    if plot_type=="Area plot": #11
        fig = px.area(df, x ,y, color=group_by)

    return fig

def one_categoric(df, col_name, group_by=None, plot_type='Histogram'):
    """
        plot type one of ['Donut', 'Pie', 'Histogram']
    """
    if plot_type is None:
        plot_type = 'Histogram'
    feat = list(df[col_name])
    if plot_type=='Donut': # 12 spasel
        fig = go.Figure(data=[go.Pie(labels=feat, hole=.4)]) 
    
    if plot_type=='Pie': # 13 spasel
        fig = go.Figure(data=[go.Pie(labels=feat)]) 

    if plot_type=='Histogram': # 14
        fig = px.histogram(df, x=col_name, color=group_by)
        fig.update_layout(bargap=0.2)

    return fig

def one_textual(df, col_name):
    text = " ".join(df[col_name].dropna().to_list())
    wordcloud = WordCloud(width=480, height=480, margin=0).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear') # 15

def one_numeric_one_categorical(df, x, y, group_by=None, plot_type="Box"):
    """
        ["Violin", "Box", "Basic Stats]
    """
    if plot_type is None:
        plot_type = "Box"

    fig = go.Figure()
    if plot_type=='Violin': # 17
        if len(y) > 1:
            for col in y:
                fig.add_trace(go.Violin(x=df[x], y=df[col], name=col))
        else:
            fig.add_trace(go.Violin(x=df[x], y=df[y[0]],name=y[0]))
        fig.update_traces(box_visible=True, meanline_visible=True)
        fig.update_layout(violinmode='group') 
    elif plot_type=='Box': # 18
        for col in y:
            fig.add_trace(go.Box(x=df[x],
                                y=df[col],
                            name=col))
                            
    elif plot_type=="Basic Stats": # 19
        tb = pd.pivot_table(df, index=x, values=y, aggfunc=['mean', 'max', 'min'])
        tb.columns=['_'.join([str(i) for i in tb.columns[j]]) for j in range(0, tb.shape[1])]

        tb = tb.reset_index()

        cols = [i for i in list(tb.columns) if i != x]
        fig = px.bar(tb, x=x, y=cols, barmode='group')
    
    fig.update_layout(xaxis=dict(title=x, zeroline=False))
    return fig


def two_categorical(df, x, y, plot_type="Cross tab"):
    """
        ['Cross tab', "Stacked bone_numeric_one_categoricalar"]
    """
    if plot_type is None:
        plot_type = 'Cross tab'

    if plot_type == 'Stacked bar': # 20
        df_cross = pd.crosstab(df[x], df[y])
        data = []
        for x in df_cross.columns:
            data.append(go.Bar(name=str(x), x=df_cross.index, y=df_cross[x]))

        fig = go.Figure(data)
        fig.update_layout(barmode = 'stack')
        #For you to take a look at the result use

    if plot_type == "Cross tab": # 21
        df_cross = pd.crosstab(df[x], df[y])
        return df_cross
    
        
    return fig

def one_datetime_one_numeric(df, x, y, group_by=None, plot_type="Connected Scatter"):
    """
        ['Connected Scatter', "Stock price"]
    """
    if plot_type is None:
        plot_type = "Connected Scatter"
    if plot_type == "Connected Scatter": # 22
        fig = px.line(df, x, y, markers=True, color=group_by)
    if plot_type == "Stock price": # 23
        fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'])
                     ])


    return fig