import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

SIDEBAR_STYLE = {}
SIDEBAR_STYLE["position"] = "fixed"
SIDEBAR_STYLE["top"] = 0
SIDEBAR_STYLE["left"] = 0
SIDEBAR_STYLE["bottom"] = 0
SIDEBAR_STYLE["width"] = "16rem"
SIDEBAR_STYLE["padding"] = "2rem 1rem"
SIDEBAR_STYLE["background-color"] = "#f8f9fa"

TOPBAR_STYLE = {}
TOPBAR_STYLE["margin-left"] = "18rem"
TOPBAR_STYLE["margin-right"] = "2rem"
TOPBAR_STYLE["padding"] = "2rem 1rem"

CONTENT_STYLE = {}
CONTENT_STYLE["margin-left"] = "18rem"
CONTENT_STYLE["margin-right"] = "2rem"
CONTENT_STYLE["padding"] = "2rem 1rem"

sidebar = html.Div([html.H2(html.A("Application", href="/"), className="display-4"),
                    html.H6(html.A('- Ailever', href="https://github.com/ailever/ailever/wiki", target="_blank")),
                    html.Hr(),
                    html.P("Promulgate values for a better tomorrow", className="lead"),
                    dbc.Nav([dbc.NavLink("Page 1", href="/page1/1", id="side1"),
                             dbc.NavLink("Page 2", href="/page2/1", id="side2"),
                             dbc.NavLink("Page 3", href="/page3/1", id="side3"),
                             dbc.NavLink("Page 4", href="/page4/1", id="side4")],
                            vertical=True,
                            pills=True)],
                   style=SIDEBAR_STYLE)
topbar = html.Div([dbc.Nav(id='topbar', pills=False),
                   html.Hr(),                   
                   html.H2(id='topbar-title')], style=TOPBAR_STYLE)
topbars = {}
topbars['root'] = [html.Div()]
topbars['page1'] = [dbc.NavItem(dbc.NavLink("P1,T1", id='side1-top1', active=True, disabled=False, href="/page1/1")),
                    dbc.NavItem(dbc.NavLink("P1,T2", id='side1-top2', active=False, disabled=False, href="/page1/2")),
                    dbc.NavItem(dbc.NavLink("P1,T3", id='side1-top3', active=False, disabled=False, href="/page1/3")),
                    dbc.DropdownMenu([dbc.DropdownMenuItem("Item 1"), dbc.DropdownMenuItem("Item 2")], label="Dropdown", nav=True)]
topbars['page2'] = [dbc.NavItem(dbc.NavLink("P2,T1", id='side2-top1', active=True, disabled=False, href="/page2/1")),
                    dbc.NavItem(dbc.NavLink("P2,T2", id='side2-top2', active=False, disabled=False, href="/page2/2")),
                    dbc.NavItem(dbc.NavLink("P2,T3", id='side2-top3', active=False, disabled=False, href="/page2/3")),
                    dbc.DropdownMenu([dbc.DropdownMenuItem("Item 1"), dbc.DropdownMenuItem("Item 2")], label="Dropdown", nav=True)]
topbars['page3'] = [dbc.NavItem(dbc.NavLink("P3,T1", id='side3-top1', active=True, disabled=False, href="/page3/1")),
                    dbc.NavItem(dbc.NavLink("P3,T2", id='side3-top2', active=False, disabled=False, href="/page3/2")),
                    dbc.NavItem(dbc.NavLink("P3,T3", id='side3-top3', active=False, disabled=False, href="/page3/3")),
                    dbc.DropdownMenu([dbc.DropdownMenuItem("Item 1"), dbc.DropdownMenuItem("Item 2")], label="Dropdown", nav=True)]
topbars['page4'] = [dbc.NavItem(dbc.NavLink("P4,T1", id='side4-top1', active=True, disabled=False, href="/page4/1")),
                    dbc.NavItem(dbc.NavLink("P4,T2", id='side4-top2', active=False, disabled=False, href="/page4/2")),
                    dbc.NavItem(dbc.NavLink("P4,T3", id='side4-top3', active=False, disabled=False, href="/page4/3")),
                    dbc.DropdownMenu([dbc.DropdownMenuItem("Item 1"), dbc.DropdownMenuItem("Item 2")], label="Dropdown", nav=True)]
content = html.Div(id="page-content", style=CONTENT_STYLE)

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([dcc.Location(id="url"), sidebar, topbar, content])


##############################################################################################################################################################################################

O = {}
O['P,T,0,0'] = dcc.Markdown("""
## Ailever App materials URL
- [FinanceDataReader](https://github.com/FinanceData/FinanceDataReader/wiki/Users-Guide)
- [Investopedia](https://www.investopedia.com/)
- [Investing](https://www.investing.com/)
""")

page_layouts = {}
page_layouts['/'] = html.Div([dbc.Row([dbc.Col(O['P,T,0,0'], width=12)])])
page_layouts['/page1/1'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page1/2'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page1/3'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page2/1'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page2/2'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page2/3'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page3/1'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page3/2'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page3/3'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page4/1'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page4/2'] = html.Div([dbc.Row([dbc.Col(width=12)])])
page_layouts['/page4/3'] = html.Div([dbc.Row([dbc.Col(width=12)])])




# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback([Output(f"side{i}", "active") for i in range(1,5)],
              Output("topbar", "children"),
              Output("topbar-title", "children"),
              Input("url", "pathname"))
def side_toggle_active_links(pathname):
    if pathname == "/":
        outs = []
        side_toggle = [False]*4
        topbar = topbars['root']
        topbar_title = None
        outs.extend(side_toggle)
        outs.append(topbar)
        outs.append(topbar_title)
        return outs
    outs = []
    side_toggle = [pathname[:6] == f"/page{i}" for i in range(1,5)]
    topbar = topbars[pathname[1:6]]
    topbar_title = f'TITLE {pathname[5:6]}, {pathname[7:8]}'
    outs.extend(side_toggle)
    outs.append(topbar)
    outs.append(topbar_title)
    return outs

@app.callback(Output("page-content", "children"),
              [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/" : return page_layouts['/']
    elif pathname == "/page1/1" : return page_layouts['/page1/1']
    elif pathname == "/page1/2" : return page_layouts['/page1/2']
    elif pathname == "/page1/3" : return page_layouts['/page1/3']
    elif pathname == "/page2/1" : return page_layouts['/page2/1']
    elif pathname == "/page2/2" : return page_layouts['/page2/2']
    elif pathname == "/page2/3" : return page_layouts['/page2/3']
    elif pathname == "/page3/1" : return page_layouts['/page3/1']
    elif pathname == "/page3/2" : return page_layouts['/page3/2']
    elif pathname == "/page3/3" : return page_layouts['/page3/3']
    elif pathname == "/page4/1" : return page_layouts['/page4/1']
    elif pathname == "/page4/2" : return page_layouts['/page4/2']
    elif pathname == "/page4/3" : return page_layouts['/page4/3']
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


class Application():
    def run(self, host='127.0.0.1', port='8050'):
        app.run_server(host=host, port=port, debug=True)

App = Application()



if __name__ == "__main__":
    App.run()
