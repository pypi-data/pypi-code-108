import numpy as _np

import dash_core_components as _dcc
import dash_html_components as _html
import dash_bootstrap_components as _dbc


from dash.dependencies import Input as _Input
from dash.dependencies import Output as _Output
from dash.dependencies import State as _State

import json as _json
import dash as _dash
import dask.dataframe as _dd


class DfFilter:

    """
    initialize the filter with the dataframe to work with
    """

    def __init__(self, df, name, publicCols=None, title=None):

        # assume publicCols is not maintained yet and skip it
        if(publicCols is not None and len(publicCols) == 0):
            publicCols = None

        self.df = df
        self._name = name

        # the title can differ from the name
        self._title = name
        if title:
            self._title = title

        # analyze data for numerical and categorical variables
        # create a list of possible continous values
        self.numerical_Cols = [i for i in self.df.columns if self.df[i].dtype in (
            _np.float32,  _np.float64, _np.int32,  _np.int64) and (publicCols is None or i in publicCols)]
        self.numerical_Min = {}
        self.numerical_Max = {}

        for n in self.numerical_Cols:
            self.numerical_Min[n] = self.df[n].dropna().min()
            self.numerical_Max[n] = self.df[n].dropna().max()

        # create a list of categorical columns
        self.categorical_Cols = [i for i in self.df.columns if not self.df[i].dtype in (
            _np.float32,  _np.float64, _np.int32,  _np.int64) and (publicCols is None or i in publicCols)]
        self.category_Dict = {}

        for n in self.categorical_Cols:
            self.category_Dict[n] = self.df[n].unique()

        # all columns
        self.all_Cols = [i for i in self.df.columns if (
            publicCols is None or i in publicCols)]

        if isinstance(self.df, _dd.DataFrame):
            for k in self.numerical_Min:
                self.numerical_Min[k] = self.numerical_Min[k].compute(
                    scheduler='single-threaded')
            for k in self.numerical_Max:
                self.numerical_Max[k] = self.numerical_Max[k].compute(
                    scheduler='single-threaded')
            for k in self.categorical_Cols:
                self.category_Dict[k] = self.category_Dict[k].compute(
                    scheduler='single-threaded')

        # make simple python lists
        for n in self.categorical_Cols:
            self.category_Dict[n] = list(self.category_Dict[n])

        # define a variable to change the filter columns
        self.filter_Cols = [c for c in self.all_Cols if
                            not ("date" in c) and (
                                (c in self.categorical_Cols and len(self.category_Dict[c]) > 0 and len(self.category_Dict[c]) < 5000) or
                                (c in self.numerical_Cols and self.numerical_Min[c] != self.numerical_Max[c])
                            )
                            ]

        # the input and state variables can be used for a callback
        self.Input = None
        self.State = None

    """
    create a filter section to add to the layout
    """

    def get_layout(self):
        layout = _dbc.Card(_dbc.CardBody([
            _html.Label(
                self._title, className="highlightLabel card-collaps-label"),
            _dcc.Dropdown(
                id=self._name+'-CatDropdown',
                options=[{'label': d, 'value': d} for d in self.filter_Cols]
            ),
            _html.Div([

                _html.Div([
                    _html.Label("Filter Range", className="simpleLabel"),
                    _html.Div([
                        _html.Div([_html.Span(
                            "Min", className="input-group-text")], className="input-group-prepend"),
                        _dbc.Input(id=self._name+"-min",
                                   type="number",  className="form-control"),
                        _html.Div(
                            [_html.Span("Max", className="input-group-text")], className="input-group-append"),
                        _dbc.Input(id=self._name+"-max",
                                   type="number",  className="form-control")
                    ], className="input-group mb-3 input-group-sm")
                ], id=self._name+'-numeric-div', style={'display': 'none'}
                ),
                _html.Div([
                    _dcc.RadioItems(
                        options=[
                            {'label': 'include', 'value': 'include'},
                            {'label': 'exclude', 'value': 'exclude'}
                        ],
                        value='include',
                        id=self._name+"-includeExclude",
                        className="text-center"
                    ),
                    _dcc.Dropdown(
                        options=[],
                        multi=True,
                        id=self._name+"-options"
                    )
                ], id=self._name+'-cat-div', style={'display': 'none'}),
            ], style={"min-height": "70px"}),


            _html.Div([
                _html.Button(
                    "Apply",
                    id=self._name+"-add",
                    className="btn btn-outline-light"
                ),
                _html.Button(
                    "Remove",
                    id=self._name+"-remove",
                    className="btn btn-outline-light"
                ),
                _html.Button(
                    "Clear",
                    id=self._name+"-clear",
                    className="btn btn-outline-light"
                )],
                className="btn-group special btn-group-sm", role="group"
            ),

            _html.Label("Instructions", className="highlightLabel"),
            _dbc.Card(_dbc.CardBody([
                _dcc.Markdown(
                    id=self._name+'-desc',
                    className="lightAndSmall"
                ),
                _dcc.Textarea(
                    id=self._name+'-state',
                    hidden="true"
                )]), style={"height": "100px", "overflow-y": "scroll"}),
            _dcc.Store(id=self._name+'-initial-state')
        ]), className="card-collapsed")

        self.Input = _Input(self._name+'-state', 'value')
        self.State = _State(self._name+'-state', 'value')
        self.InitialState = _Output(self._name+'-initial-state', 'data')
        return layout

    """
    helper to compute the user readable filter config
    """

    def getFilterText(self, filter_state):
        listOutput = ""
        for f in filter_state:
            if f["type"] == "minmax":
                listOutput = listOutput + \
                    "**{1}** in \[{2}, {3}\]  \n".format(
                        1, f["var"], f["min"], f["max"])
            if f["type"] == "include":
                listOutput = listOutput + \
                    "**{1}** in {{{2}}}  \n".format(1,
                                                    f["var"], ", ".join(f["values"]))
            if f["type"] == "exclude":
                listOutput = listOutput + \
                    "**{1}** not in {{{2}}}  \n".format(
                        1, f["var"], ", ".join(f["values"]))

        return listOutput

    """
    register the filter callbacks to the dashapp
    """

    def register_callbacks(self, dashapp):
        """
        update the filter content once a button is pressed
        """
        @dashapp.callback(
            [
                _Output(self._name+'-desc', 'children'),
                _Output(self._name+'-state', 'value')
            ],
            [
                _Input(self._name+'-add', 'n_clicks'),
                _Input(self._name+'-remove', 'n_clicks'),
                _Input(self._name+'-clear', 'n_clicks'),

                _Input(self._name+'-initial-state', 'data'),
            ],
            [
                _State(self._name+'-state', 'value'),
                _State(self._name+'-CatDropdown', 'value'),
                _State(self._name+'-min', 'value'),
                _State(self._name+'-max', 'value'),

                _State(self._name+'-includeExclude', 'value'),
                _State(self._name+'-options', 'value'),
            ],
        )
        def update_filter_content(add_clicks, remove_clicks, clear_clicks,
                                  initial_state,

                                  filter_state_string,
                                  filter_var_string,
                                  min_value,
                                  max_value,
                                  includeExclude,
                                  optionValues
                                  ):

            ctx = _dash.callback_context

            # check if the update is triggered by the initial_state
            if ctx.triggered:
                if ctx.triggered[0]['prop_id'] == self._name+"-initial-state.data":
                    if initial_state != None and len(initial_state) > 2:
                        filter_state = _json.loads(initial_state)
                        return self.getFilterText(filter_state), _json.dumps(filter_state)
                    else:
                        return "", "{}"

            if ctx.triggered:
                button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if button_id == self._name+"-clear":
                    filter_state = []
                    return "", _json.dumps(filter_state)

            if filter_var_string == None:
                return "", "{}"
                #raise Exception("no variable name")

            if filter_state_string is not None:
                filter_state = [f for f in _json.loads(
                    filter_state_string) if f["var"] != filter_var_string]
            else:
                filter_state = []

            if ctx.triggered:
                if button_id == self._name+"-add":
                    if(filter_var_string in self.numerical_Cols):
                        filter_state.append(dict(
                            type="minmax",
                            var=filter_var_string,
                            min=min_value,
                            max=max_value
                        ))
                    else:
                        filter_state.append(dict(
                            type=includeExclude,
                            var=filter_var_string,
                            values=optionValues
                        ))

            return self.getFilterText(filter_state), _json.dumps(filter_state)

        """
        update the filter content if a new filter variable is selected
        """
        @dashapp.callback([
            _Output(self._name+'-min', 'value'),
            _Output(self._name+'-max', 'value'),
            _Output(self._name+'-options', 'options'),
            _Output(self._name+'-numeric-div', 'style'),
            _Output(self._name+'-cat-div', 'style'),
        ],
            [
            _Input(self._name+'-CatDropdown', 'value'),
        ])
        def change_dropdown(filterCatDropdown_value):

            minval = None
            maxval = None

            if(filterCatDropdown_value in self.numerical_Cols):
                try:

                    options = [{'label': 'NA', 'value': 'NA'}]
                    numDivStyle = {}
                    catDivStyle = {'display': 'none'}

                    minval = self.numerical_Min[filterCatDropdown_value]
                    maxval = self.numerical_Max[filterCatDropdown_value]

                    print(f"min {minval}   max {maxval}")

                    digits = int(5-_np.log10(maxval - minval))
                    print(digits)

                    minval = round(minval, digits)
                    maxval = round(maxval, digits)

                except:
                    pass

            else:
                if filterCatDropdown_value in self.category_Dict:
                    minval = None
                    maxval = None
                    options = [{'label': x, 'value': x}
                               for x in self.category_Dict[filterCatDropdown_value]]
                    catDivStyle = {}
                    numDivStyle = {'display': 'none'}
                else:
                    minval = None
                    maxval = None
                    options = []
                    catDivStyle = {'display': 'none'}
                    numDivStyle = {'display': 'none'}

            return minval, maxval, options, numDivStyle, catDivStyle

    def getDataframe(self, filterConfig):
        output = self.df

        # check if filter defined
        if filterConfig != None:
            filterData = filterConfig
            # json parse the filter config if needed
            if isinstance(filterConfig, str):
                filterData = _json.loads(filterConfig)

            # apply all filters
            for f in filterData:
                if(f['type'] == "include"):
                    output = output[output[f['var']].isin(f['values'])]
                if(f['type'] == "exclude"):
                    output = output[~output[f['var']].isin(f['values'])]
                if(f['type'] == "minmax"):
                    output = output[(output[f['var']] >= f['min']) & (
                        output[f['var']] <= f['max'])]

        # return the filtered dataframe
        return output
