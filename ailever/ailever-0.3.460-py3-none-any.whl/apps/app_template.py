from urllib.request import urlretrieve
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2(html.A("Ailever", href="/"), className="display-4"),
        html.Hr(),
        html.P(
            "Promulgate values for a better tomorrow", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


contents = {}
contents['root'] = {}
contents['page1'] = {}
contents['page2'] = {}
contents['page3'] = {}

##############################################################################################################################################################################################
contents['root'] = dcc.Markdown("""
## Ailever App materials URL
- [FinanceDataReader](https://github.com/FinanceData/FinanceDataReader/wiki/Users-Guide)
- [Investopedia](https://www.investopedia.com/)
- [Investing](https://www.investing.com/)
""")
##############################################################################################################################################################################################
contents['page1']['tab1'] = [html.P("This is tab 1!", className="card-text"),
                             dbc.Button("Click here", color="success")]
##############################################################################################################################################################################################
contents['page1']['tab2'] = [html.P("This is tab 2!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
##############################################################################################################################################################################################
contents['page1']['tab3'] = [html.P("This is tab 3!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
##############################################################################################################################################################################################
contents['page2']['tab1'] = [html.P("This is tab 1!", className="card-text"),
                             dbc.Button("Click here", color="success")]
##############################################################################################################################################################################################
contents['page2']['tab2'] = [html.P("This is tab 2!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
##############################################################################################################################################################################################
contents['page2']['tab3'] = [html.P("This is tab 3!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
##############################################################################################################################################################################################
contents['page3']['tab1'] = [html.P("This is tab 1!", className="card-text"),
                             dbc.Button("Click here", color="success")]
##############################################################################################################################################################################################
contents['page3']['tab2'] = [html.P("This is tab 2!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
##############################################################################################################################################################################################
contents['page3']['tab3'] = [html.P("This is tab 3!", className="card-text"),
                             dbc.Button("Don't click here", color="danger")]
##############################################################################################################################################################################################

page_layouts = {}
page_layouts['/'] = html.P("This is the content of main page!")
page_layouts['/page-1'] = dbc.Tabs([dbc.Tab(dbc.Card(dbc.CardBody(contents['page1']['tab1'])), label="Tab 1", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page1']['tab2'])), label="Tab 2", disabled=False),
                                    dbc.Tab(dbc.Card(dbc.CardBody(contents['page1']['tab3'])), label="Tab 3", disabled=True)])
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



class [AileverApp]():
    def __init__(self):
        pass

    def download(self):
        urlretrieve('https://raw.githubusercontent.com/ailever/ailever/master/ailever/apps/[AileverApp].py', f'./[AileverApp].py')

    def run(self):
        app.run_server(host="127.0.0.1", port='8050', debug=True)

[aileverapp] = [AileverApp]()

