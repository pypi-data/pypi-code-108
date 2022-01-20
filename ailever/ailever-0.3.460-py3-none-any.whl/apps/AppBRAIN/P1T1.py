import plotly.express as px
import pandas as pd

from .BRAINApp import app
#from BRAINApp import app
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

class Components(dict):
    def __init__(self):
        self['0,0'] = None
        self['0,1'] = None
        self['1,0'] = None
        self['1,1'] = None
        self['2,0'] = None
        self['2,1'] = None

    def updateR0C0(self):
        df = px.data.iris()
        self['0,0'] = px.parallel_coordinates(df, color="species_id", labels={"species_id": "Species",
                "sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
                "petal_width": "Petal Width", "petal_length": "Petal Length", },
                             color_continuous_scale=px.colors.diverging.Tealrose,
                             color_continuous_midpoint=2)
        self['0,0'] = dcc.Graph(figure=self['0,0'])

    def updateR0C1(self):
        df = px.data.medals_wide(indexed=True)
        self['0,1'] = px.imshow(df)
        self['0,1'] = dcc.Graph(figure=self['0,1'])

    def updateR1C0(self):
        df = pd.DataFrame(dict(r=[1, 5, 2, 2, 3],
                               theta=['processing cost','mechanical properties','chemical stability','thermal stability', 'device integration']))
        self['1,0'] = px.line_polar(df, r='r', theta='theta', line_close=True)
        self['1,0'] = dcc.Graph(figure=self['1,0'])

    def updateR1C1(self):
        self['1,1'] = cyto.Cytoscape(id='cytoscape',
                                     elements=[
                {'data': {'id': 'ca', 'label': 'Canada'}}, 
                {'data': {'id': 'on', 'label': 'Ontario'}}, 
                {'data': {'id': 'qc', 'label': 'Quebec'}},
                {'data': {'source': 'ca', 'target': 'on'}}, 
                {'data': {'source': 'ca', 'target': 'qc'}}
            ],
            layout={'name': 'breadthfirst'},
            style={'width': '400px', 'height': '500px'}
        )

    def updateR2C0(self):
        df = px.data.wind()
        self['2,0'] = px.bar_polar(df, r="frequency", theta="direction",
                   color="strength", template="plotly_dark",
                   color_discrete_sequence= px.colors.sequential.Plasma_r)
        self['2,0'] = dcc.Graph(figure=self['2,0'])

    def updateR2C1(self):
        df = px.data.gapminder()
        animations = {
            'Scatter': px.scatter(
                df, x="gdpPercap", y="lifeExp", animation_frame="year", 
                animation_group="country", size="pop", color="continent", 
                hover_name="country", log_x=True, size_max=55, 
                range_x=[100,100000], range_y=[25,90]),
            'Bar': px.bar(
                df, x="continent", y="pop", color="continent", 
                animation_frame="year", animation_group="country", 
                range_y=[0,4000000000]),
        }
        self['2,1'] = html.Div([
            html.P("Select an animation:"),
            dcc.RadioItems(
                id='selection',
                options=[{'label': x, 'value': x} for x in animations],
                value='Scatter'
            ),
            dcc.Graph(id="graph"),
        ])


# R2C1
df = px.data.gapminder()
animations = {
    'Scatter': px.scatter(
        df, x="gdpPercap", y="lifeExp", animation_frame="year", 
        animation_group="country", size="pop", color="continent", 
        hover_name="country", log_x=True, size_max=55, 
        range_x=[100,100000], range_y=[25,90]),
    'Bar': px.bar(
        df, x="continent", y="pop", color="continent", 
        animation_frame="year", animation_group="country", 
        range_y=[0,4000000000]),
}

@app.callback(
    Output("graph", "figure"), 
    [Input("selection", "value")])
def display_animated_graph(s):
    return animations[s]

