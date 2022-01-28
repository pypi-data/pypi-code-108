import FinanceDataReader as fdr
from datetime import datetime
import os
import copy
import numpy as np
import pandas as pd
import statsmodels.tsa.api as smt

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = dash.Dash(suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {"position": "fixed",
                 "top": 0,
                 "left": 0,
                 "bottom": 0,
                 "width": "16rem",
                 "padding": "2rem 1rem",
                 "background-color": "#f8f9fa"}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {"margin-left": "18rem",
                 "margin-right": "2rem",
                 "padding": "2rem 1rem"}

sidebar = html.Div([html.H2(html.A("Eyes", href="/"), className="display-4"),
                    html.H6(html.A('- Ailever', href="https://github.com/ailever/ailever/wiki", target="_blank")),
                    html.Hr(),
                    html.P("Promulgate values for a better tomorrow", className="lead"),
                    dbc.Nav([dbc.NavLink("FINANCIAL MARKETS", href="/page-1", id="page-1-link"),
                             dbc.NavLink("FINANCIAL STATEMENTS", href="/page-2", id="page-2-link"),
                             dbc.NavLink("Page 3", href="/page-3", id="page-3-link")],
                             vertical=True, pills=True)],
                    style=SIDEBAR_STYLE)

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


contents = {}
contents['root'] = {}
contents['page1'] = {}
contents['page2'] = {}
contents['page3'] = {}

contents['root'] = dcc.Markdown("""
## Finance materials URL
- [FinanceDataReader](https://github.com/FinanceData/FinanceDataReader/wiki/Users-Guide)
- [Investopedia](https://www.investopedia.com/)
- [Investing](https://www.investing.com/)
""")


variables = {}
variables['page1'] = {}
variables['page2'] = {}
variables['page3'] = {}
variables['page1']['tab1'] = {} 
variables['page1']['tab2'] = {}
variables['page1']['tab3'] = {}


##############################################################################################################################################################################################


today = datetime.today()
df = {}
markets = ['NYSE', 'NASDAQ', 'AMEX', 'KRX', 'KOSPI', 'KOSDAQ', 'KONEX', 'KRX-DELISTING', 'KRX-ADMINISTRATIVE', 'SSE', 'SZSE', 'HKEX', 'TSE', 'HOSE']
for market in markets:
    if not os.path.isfile(f'{market}.csv'):
        try:
            fdr.StockListing(market).to_csv(f'{market}.csv')
            df[f'{market}'] = pd.read_csv(f'{market}.csv').drop('Unnamed: 0', axis=1)
        except:
            pass
    else:
        df[f'{market}'] = pd.read_csv(f'{market}.csv').drop('Unnamed: 0', axis=1)

variables['page1']['tab1']['dataframe'] = df
variables['page1']['tab1']['markets'] = markets
contents['page1']['tab1'] = [html.Div([dcc.RadioItems(id="market",
                                                      options=[{'label':market, 'value':market} for market in markets],
                                                      value='NYSE'),
                                       dcc.Dropdown(id='company',
                                                    options=[{"label": x, "value": x} for x in df['NYSE'].Name],
                                                    value='Goldman Sachs Group Inc',
                                                    clearable=False),
                                       html.Br(),
                                       html.H2("Time Series"),
                                       dcc.RadioItems(id="plot-type",
                                                      options=[{'label': 'Line', 'value':'L'},
                                                               {'label': 'Scatter', 'value':'S'}],
                                                      value='L'),
                                       dcc.Graph(id='graph1'),
                                       html.H4("Time Series : Auto-Correlation"),
                                       dcc.Graph(id='graph2'),
                                       dcc.Graph(id='graph3'),
                                       html.H2("Difference"),
                                       dcc.Graph(id='graph4'),
                                       html.H4("Difference : Auto-Correlation"),
                                       dcc.Graph(id='graph5'),
                                       dcc.Graph(id='graph6')])]

@app.callback(
    Output('company', 'options'),
    Output('company', 'value'),
    Input('market', 'value')
)
def stock_market(market):
    value = df[f'{market}'].Name.iloc[0]
    options = [{"label": x, "value": x} for x in df[f'{market}'].Name]
    return options, value

@app.callback(
    Output('graph1', "figure"),
    Output('graph2', "figure"),
    Output('graph3', "figure"),
    Output('graph4', "figure"),
    Output('graph6', "figure"),
    Output('graph5', "figure"),
    Input('market', "value"),
    Input('company', "value"),
    Input('plot-type', "value"),
)
def display_timeseries(market, company, plot_type):
    stock_info = df[f'{market}'][df[f'{market}'].Name==company]
    symbol = str(stock_info.Symbol.values[0])
    price = fdr.DataReader(symbol, exchange=market)
    stock_df = price
    time_series = stock_df['Close']

    # FIG1
    if plot_type == 'L':
        fig1 = px.line(stock_df.reset_index(), x='Date', y='Close')
        fig1.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                           dict(count=3, label="3m", step="month", stepmode="backward"),
                                                           dict(count=6, label="6m", step="month", stepmode="backward"),
                                                           dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                           dict(count=1, label="1y", step="year", stepmode="backward"),
                                                           dict(count=3, label="3y", step="year", stepmode="backward"),
                                                           dict(count=5, label="5y", step="year", stepmode="backward"),
                                                           dict(step="all")])))
    elif plot_type == 'S':
        fig1 = px.scatter(stock_df['Close'], trendline='ols', title=f'{company}')
        fig1.update_xaxes(rangeslider_visible=True,
                          rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                           dict(count=3, label="3m", step="month", stepmode="backward"),
                                                           dict(count=6, label="6m", step="month", stepmode="backward"),
                                                           dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                           dict(count=1, label="1y", step="year", stepmode="backward"),
                                                           dict(count=3, label="3y", step="year", stepmode="backward"),
                                                           dict(count=5, label="5y", step="year", stepmode="backward"),
                                                           dict(step="all")])))

    # FIG2
    ACF = smt.acf(time_series, alpha=0.05)[0]
    ACF_LOWER = smt.acf(time_series, alpha=0.05)[1][:, 0]
    ACF_UPPER = smt.acf(time_series, alpha=0.05)[1][:, 1]
    ACF_DF = pd.DataFrame(data={'acf':ACF, 'acf_lower':ACF_LOWER, 'acf_upper':ACF_UPPER})

    acf = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf'],
        mode = 'lines',
        name = 'ACF(MA)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    acf_lower = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    acf_upper = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [acf, acf_lower, acf_upper]
    fig2 = go.Figure(data = data)

    # FIG3
    PACF = smt.pacf(time_series, alpha=0.05)[0]
    PACF_LOWER = smt.pacf(time_series, alpha=0.05)[1][:, 0]
    PACF_UPPER = smt.pacf(time_series, alpha=0.05)[1][:, 1]
    PACF_DF = pd.DataFrame(data={'pacf':PACF, 'pacf_lower':PACF_LOWER, 'pacf_upper':PACF_UPPER})

    pacf = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf'],
        mode = 'lines',
        name = 'PACF(AR)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    pacf_lower = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    pacf_upper = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [pacf, pacf_lower, pacf_upper]
    fig3 = go.Figure(data = data)

    # FIG4
    fig4 = px.line(stock_df.diff().reset_index(), x='Date', y='Close')
    fig4.update_xaxes(rangeslider_visible=True,
                      rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                       dict(count=3, label="3m", step="month", stepmode="backward"),
                                                       dict(count=6, label="6m", step="month", stepmode="backward"),
                                                       dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                       dict(count=1, label="1y", step="year", stepmode="backward"),
                                                       dict(count=3, label="3y", step="year", stepmode="backward"),
                                                       dict(count=5, label="5y", step="year", stepmode="backward"),
                                                       dict(step="all")])))

    # FIG5
    ACF = smt.acf(time_series.diff().dropna(), alpha=0.05)[0]
    ACF_LOWER = smt.acf(time_series.diff().dropna(), alpha=0.05)[1][:, 0]
    ACF_UPPER = smt.acf(time_series.diff().dropna(), alpha=0.05)[1][:, 1]
    ACF_DF = pd.DataFrame(data={'acf':ACF, 'acf_lower':ACF_LOWER, 'acf_upper':ACF_UPPER})

    acf = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf'],
        mode = 'lines',
        name = 'ACF(MA)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    acf_lower = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    acf_upper = go.Scatter(
        x = ACF_DF.index,
        y = ACF_DF['acf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [acf, acf_lower, acf_upper]
    fig5 = go.Figure(data = data)

    # FIG6
    PACF = smt.pacf(time_series.diff().dropna(), alpha=0.05)[0]
    PACF_LOWER = smt.pacf(time_series.diff().dropna(), alpha=0.05)[1][:, 0]
    PACF_UPPER = smt.pacf(time_series.diff().dropna(), alpha=0.05)[1][:, 1]
    PACF_DF = pd.DataFrame(data={'pacf':PACF, 'pacf_lower':PACF_LOWER, 'pacf_upper':PACF_UPPER})

    pacf = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf'],
        mode = 'lines',
        name = 'PACF(AR)',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 255)', width = 2),
        connectgaps = True
    )
    pacf_lower = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_lower'],
        mode = 'lines',
        name = 'Lower bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )
    pacf_upper = go.Scatter(
        x = PACF_DF.index,
        y = PACF_DF['pacf_upper'],
        mode = 'lines',
        name = 'Upper bound',
        line = dict(shape = 'linear', color = 'rgb(0, 0, 0)', width = 2, dash = 'dot'),
        connectgaps = True
    )

    data = [pacf, pacf_lower, pacf_upper]
    fig6 = go.Figure(data = data)

    return fig1, fig2, fig3, fig4, fig5, fig6


##############################################################################################################################################################################################


df2 = copy.deepcopy(variables['page1']['tab1']['dataframe'])

market = 'KRX'
companies = ['삼성전자', 'LG전자', 'SK하이닉스', 'DB하이텍', 'LG디스플레이', 'NH투자증권', 'SK증권', '삼성증권', 'CJ제일제당']
query_string = f"Name in {companies}"
stock_infos = df2[f'{market}'].query(query_string)
symbols = stock_infos.Symbol
companies = stock_infos.Name.tolist()   # re-define company for ordering
previous_companies = np.array(companies)

stock_df = {}
init_layout = (3,3)
fig = make_subplots(rows=init_layout[0], cols=init_layout[1], subplot_titles=companies)
fig.update_layout(height=700,
                  margin=dict(l=20, r=20, t=50, b=20))
fig.update_xaxes(rangeselector=dict(buttons=list([dict(count=1, label="1m", step="month", stepmode="backward"),
                                                 dict(count=3, label="3m", step="month", stepmode="backward"),
                                                 dict(count=6, label="6m", step="month", stepmode="backward"),
                                                 dict(count=1, label="YTD", step="year", stepmode="todate"),
                                                 dict(count=1, label="1y", step="year", stepmode="backward"),
                                                 dict(count=3, label="3y", step="year", stepmode="backward"),
                                                 dict(count=5, label="5y", step="year", stepmode="backward"),
                                                 dict(step="all")])))

for i, (symbol, company) in enumerate(zip(symbols, companies)):
    stock_df[company] = fdr.DataReader(symbol, exchange=market)['Close'].reset_index()
    quotient = i//init_layout[0]
    reminder = i%init_layout[0]
    fig.add_trace(go.Scatter(x=stock_df[company]['Date'], y=stock_df[company]['Close'], mode='lines+markers'), row=quotient+1, col=reminder+1)

contents['page1']['tab2'] = [html.Div([dcc.Markdown('## Technical Analysis'),                                        
                                       dcc.Slider(id='fig-width', min=1, max=2, value=1.5, step=0.1,
                                                  ),
                                       dcc.Graph(figure=fig, id='longterm-graph'),
                                       dcc.Dropdown(id='companies',
                                                    options=[{"label": x, "value": x} for x in df['KRX'].Name],
                                                    value=companies,
                                                    multi=True,
                                                    clearable=False),
                                       ])]


@app.callback(
    Output('longterm-graph', 'figure'),
    Input('companies', 'value'),
    Input('fig-width', 'value'),
    State('longterm-graph', 'figure')
)
def longterm_analysis(companies, width, fig):
    global previous_companies
    current_companies = np.array(companies)
    indices = previous_companies != current_companies

    fig = go.Figure(fig)

    if np.sum(indices) == 0:
        fig.update_layout(height=width*700)
    else:
        newly_selected_companies = current_companies[indices].tolist()
        market = 'KRX'
        stock_df = {}
        query_string = f"Name in {newly_selected_companies}"
        stock_infos = df[f'{market}'].query(query_string)
        symbols = stock_infos.Symbol.values.tolist()
        subfigs = np.array(fig.data)[indices.flatten()].tolist()
        subtitles = np.array(fig['layout']['annotations'])[indices.flatten()].tolist()
        for symbol, company, fig_obj, subtitle in zip(symbols, newly_selected_companies, subfigs, subtitles):
            stock_df[company] = fdr.DataReader(symbol, exchange=market)['Close'].reset_index()
            fig_obj.x = stock_df[company]['Date']
            fig_obj.y = stock_df[company]['Close']
            subtitle['text'] = company

        previous_companies = current_companies

    return fig


##############################################################################################################################################################################################


contents['page1']['tab3'] = [html.P("This is tab 3!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
contents['page2']['tab1'] = [html.P("This is tab 1!", className="card-text"),
                             dbc.Button("Click here", color="success")]
contents['page2']['tab2'] = [html.P("This is tab 2!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
contents['page2']['tab3'] = [html.P("This is tab 3!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
contents['page3']['tab1'] = [html.P("This is tab 1!", className="card-text"),
                             dbc.Button("Click here", color="success")]
contents['page3']['tab2'] = [html.P("This is tab 2!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
contents['page3']['tab3'] = [html.P("This is tab 3!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]


page_layouts = {}
page_layouts['/'] = contents['root']
page_layouts['/page-1'] = dbc.Tabs([dbc.Tab(dbc.Card(dbc.CardBody(contents['page1']['tab1'])), label="Stock Markets", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page1']['tab2'])), label="Technical Analysis", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page1']['tab3'])), label="Real-Time Analysis", disabled=False)])
page_layouts['/page-2'] = dbc.Tabs([dbc.Tab(dbc.Card(dbc.CardBody(contents['page2']['tab1'])), label="Tab 1", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page2']['tab2'])), label="Tab 2", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page2']['tab3'])), label="Tab 3", disabled=True)])
page_layouts['/page-3'] = dbc.Tabs([dbc.Tab(dbc.Card(dbc.CardBody(contents['page3']['tab1'])), label="Tab 1", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page3']['tab2'])), label="Tab 2", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page3']['tab3'])), label="Tab 3", disabled=True)])



# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/"]:
        return page_layouts['/']
    elif pathname in ["/page-1"]:
        return page_layouts['/page-1']
    elif pathname == "/page-2":
        return page_layouts['/page-2']
    elif pathname == "/page-3":
        return page_layouts['/page-3']
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )



class Eyes():
    def run(self):
        app.run_server(host="127.0.0.1", port='8050', debug=True)

eyes = Eyes()


if __name__ == "__main__":
    eyes.run()
