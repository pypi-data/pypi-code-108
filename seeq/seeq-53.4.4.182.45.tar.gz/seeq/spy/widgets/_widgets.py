import logging
import re
from typing import Optional

import ipywidgets

from seeq.sdk import DatasourcesApi
from seeq.spy import _search
from seeq.spy._session import Session


class SeeqItemSelect(ipywidgets.VBox):
    _searching_seeq_text = 'Searching Seeq...'

    def __init__(
            self,
            title='',
            item_name='',
            item_type='',
            item_path='',
            item_description='',
            item_datasource_name='',
            item_datasource_id='',
            item_datasource_class='',
            item_archived=None,
            item_scoped_to='',
            show_fields=('Name', 'Type'),
            type_options=('Signal', 'Scalar', 'Condition', 'Asset', 'Chart', 'Metric', 'Datasource', 'Workbook',
                          'Worksheet'),
            datasource_dropdown=True,
            multi_select=False,
            results_box_rows=5,
            max_displayed_results=40,
            show_system_datasources=False,
            show_help=False,
            session: Optional[Session] = None,
            **kwargs):
        """
        An iPython widget to search for items in Seeq.

        The following properties are defined:
            selected_value : {dict or list(dict)}
                The selected value or values
            search_terms : dict
                The search terms used to to find items in Seeq
            search_results = pandas.DataFrame
                The full list of search results from Seeq

        Parameters
        ----------
        title : str
            A title for the widget, displayed above the tool
        item_type : str
            One of 'Signal', 'Condition', 'Scalar', 'Asset', 'Histogram',
            'Metric', 'Datasource', 'Workbook', or 'Worksheet' as the
            default item type. Must be listed in type_options.
        item_name : str
            A default value for the item name search term
        item_path : str
            A default value for the item search path
        item_description : str
            A default value for the item description search term
        item_datasource_name : str
            A default value for the item datasource name. If a datasource dropdown is used and
            item_datasource_name is available in the list of available Seeq datasources, it will
            be selected by default.
        item_datasource_id : str
            A default value for the item datasource id
        item_datasource_class : str
            A default value for the item datasource class
        item_archived : bool
            A default value for the item "is archived" setting
        item_scoped_to : str
            A default value for the item workbook the item is scope to
        show_fields : list, default ['Name', 'Type']
            A list indicating which fields should be shown. Options are
            ['Name', 'Type', 'Path', 'Description', 'Datasource Dropdown',
            'Datasource Name', 'Datasource ID', 'Datasource Class',
            'Archived', 'Scoped To']
            Note that if Datasource Dropdown is used in conjunction with
            Datasource Name, Datasource ID, and Datasource Class, the entry
            in Datasource Dropdown will override entries in the other fields.
        type_options : list(str)
            The options for the Types dropdown. Possible values are:
            ['Signal', 'Scalar', 'Condition', 'Asset', 'Chart', 'Metric',
             'Datasource', 'Workbook', 'Worksheet']
        datasource_dropdown : bool, default True
            Use a dropdown menu to select the appropriate datasource.
            Requires an authenticated connection to Seeq at instantiation.
        multi_select : bool, default False
            If True, multiple items can be selected and the "selected_value" will
            return a list of dicts
        results_box_rows : int
            The number of rows in the results box
        max_displayed_results : int
            The maximum number of results displayed in the results box
        show_system_datasources : bool, default False
            If True, show system datasources in the datasource dropdown. For example,
            the "Auth" datasource is a system datasource.
        show_help : bool, default False
            If True, show an accordion with help information will be displayed at the
            top of the widget.
        session : spy.Session, optional
            If supplied, the Session object (and its Options) will be used to
            store the login session state. This is useful to log in to different
            Seeq servers at the same time or with different credentials.
        **kwargs
            debug : bool, default False
                Flag for debug mode. In debug mode search terms and the list of items
                found in Seeq are printed when the search button is pressed.
            Remaining keyword arguments are passed to the VBox super class

        Examples
        --------
        Display a search and select box that:
        - has the default fields of Name and Type
        - has a hidden filter for Datasource Name == 'test data'
        - allows only one item to be selected
        >>> item_selector = SeeqItemSelect(
            item_datasource_name='test data')
        >>> display(item_selector)

        Display a search and select box that is 500 pixels wide that:
        - has fields for Name, Type, and a dropdown menu for Datasources
        - allows multiple selections
        - allows searching for signals and conditions, with a default of Signal
        >>> item_selector = SeeqItemSelect(
            show_fields=['Name', 'Type', 'Datasource Dropdown'],
            multi_select=True,
            type_options=['Signal', 'Condition'],
            item_type='Signal')
        >>> item_selector.layout.width='500px'
        >>> display(item_selector)

        Display a search and select box that:
        - has a title of "Search for Your Items Here" in HTML heading 2
        - accepts only a name
        - is limited to Signals, even though Types aren't shown
        - has a results box that is 25 lines long
        - show a maximum of 250 items in the search results
        >>> item_selector = SeeqItemSelect(
            '<H2>Search for Your Items Here</H2>',
            show_fields=['Name'],
            item_type='Signal',
            results_box_rows=25,
            max_displayed_results=250
        )
        >>> display(item_selector)


        """

        self._show_fields = show_fields
        self._seeq_item_types = type_options
        self._use_datasource_dropdown = datasource_dropdown
        self._use_multi_select = multi_select
        self._result_box_rows = results_box_rows
        self._max_displayed_results = max_displayed_results
        self._show_system_datasources = show_system_datasources
        self._show_help = show_help
        self._session = Session.validate(session)
        self._kwargs = kwargs
        _datasources = [['Select a Datasource', None]]
        _datasource_dropdown_disabled = False
        _system_datasources = ['Auth']
        if datasource_dropdown:
            if self._session.client and self._session.client.auth_token:
                datasources_api = DatasourcesApi(self._session.client)
                request_limit = 1000
                request_page = 0
                while True:
                    datasources_output = datasources_api.get_datasources(offset=request_page, limit=request_limit)
                    for ds in datasources_output.datasources:
                        if ds.datasource_class in _system_datasources and not show_system_datasources:
                            continue
                        _datasources.append([f'{ds.name} ({ds.datasource_class})', ds])
                    if len(datasources_output.datasources) < request_limit:
                        break
                    request_page += request_limit
            else:
                _datasources = [['Error Retrieving Datasources', None]]
                _datasource_dropdown_disabled = True

        self._found_seeq_items = None
        if 'debug' in kwargs:
            self._debug = kwargs.get('debug')
            del kwargs['debug']
        else:
            self._debug = False

        # Initialize Widgets
        # Item name
        self._name_box = ipywidgets.Text(
            placeholder='Search Name',
            layout=ipywidgets.Layout(width='auto', grid_area='namebox')
        )
        if item_name and isinstance(item_name, str):
            self._name_box.value = item_name
        if 'Name' not in show_fields:
            self._name_box.layout.display = 'none'
        # Item type
        self._type_box = ipywidgets.Dropdown(
            description="",
            placeholder='Item Type',
            options=['Any Type'] + list(self._seeq_item_types),
            layout=ipywidgets.Layout(width='auto', grid_area='typebox')
        )
        if item_type and isinstance(item_type, str):
            self._type_box.value = item_type
        if 'Type' not in show_fields:
            self._type_box.layout.display = 'none'
        # Item path
        self._path_box = ipywidgets.Text(
            placeholder='Asset Path',
            layout=ipywidgets.Layout(width='auto', grid_area='pathbox')
        )
        if item_path and isinstance(item_path, str):
            self._path_box.value = item_path
        if 'Path' not in show_fields:
            self._path_box.layout.display = 'none'
        # Item description
        self._description_box = ipywidgets.Text(
            placeholder='Description',
            layout=ipywidgets.Layout(width='auto', grid_area='descriptionbox')
        )
        if item_description and isinstance(item_description, str):
            self._description_box.value = item_description
        if 'Description' not in show_fields:
            self._description_box.layout.display = 'none'
        # Item datasource dropdown
        self._datasource_dropdown = ipywidgets.Dropdown(
            description="",
            options=_datasources,
            disabled=_datasource_dropdown_disabled,
            layout=ipywidgets.Layout(width='auto', grid_area='datasourcedropdown')
        )
        # Set the default value if possible
        ds_keys, ds_values = zip(*_datasources)
        ds_keys = list(ds_keys)
        ds_values = list(ds_values)
        if item_datasource_name in ds_keys:
            self._datasource_dropdown.value = ds_values[ds_keys.index(item_datasource_name)]
        if 'Datasource Dropdown' not in show_fields:
            self._datasource_dropdown.layout.display = 'none'
        # Item datasource name
        self._datasource_name_box = ipywidgets.Text(
            placeholder='Datasource Name',
            layout=ipywidgets.Layout(width='auto', grid_area='datasourcenamebox')
        )
        if item_datasource_name and isinstance(item_datasource_name, str):
            self._datasource_name_box.value = item_datasource_name
        if 'Datasource Name' not in show_fields:
            self._datasource_name_box.layout.display = 'none'
        # Item datasource ID
        self._datasource_id_box = ipywidgets.Text(
            placeholder='Datasource ID',
            layout=ipywidgets.Layout(width='auto', grid_area='datasourceidbox')
        )
        if item_datasource_id and isinstance(item_datasource_id, str):
            self._datasource_id_box.value = item_datasource_id
        if 'Datasource ID' not in show_fields:
            self._datasource_id_box.layout.display = 'none'
        # Item datasource class
        self._datasource_class_box = ipywidgets.Text(
            placeholder='Datasource Class',
            layout=ipywidgets.Layout(width='auto', grid_area='datasourceclassbox')
        )
        if item_datasource_class and isinstance(item_datasource_class, str):
            self._datasource_class_box.value = item_datasource_class
        if 'Datasource Class' not in show_fields:
            self._datasource_class_box.layout.display = 'none'
        # Item scope
        self._scopedto_box = ipywidgets.Text(
            placeholder='Workbook Scope',
            layout=ipywidgets.Layout(width='auto', grid_area='scopedtobox')
        )
        if item_scoped_to and isinstance(item_scoped_to, str):
            self._scopedto_box.value = item_scoped_to
        if 'Scoped To' not in show_fields:
            self._scopedto_box.layout.display = 'none'
        # Item archived
        self._archived_bool = ipywidgets.Checkbox(
            description='Include Archived Items',
            layout=ipywidgets.Layout(width='auto', grid_area='archivedbox')
        )
        if item_archived is not None and isinstance(item_archived, bool):
            self._archived_bool.value = item_archived
        if 'Archived' not in show_fields:
            self._archived_bool.layout.display = 'none'

        self._search_button = ipywidgets.Button(
            description='Search',
            layout=ipywidgets.Layout(width='auto', grid_area='searchbutton', justify_self='start')
        )
        if multi_select:
            self._result_box = ipywidgets.SelectMultiple(
                placeholder='Search Results',
                rows=self._result_box_rows,
                layout=ipywidgets.Layout(width='auto', grid_area='resultsbox')
            )
        else:
            self._result_box = ipywidgets.Select(
                placeholder='Search Results',
                rows=self._result_box_rows,
                layout=ipywidgets.Layout(width='auto', grid_area='resultsbox')
            )

        self.title = ipywidgets.HTML(value=title)
        if not title:
            self.title.layout.display = 'none'

        self._help_text = ipywidgets.VBox(
            children=[
                ipywidgets.HTML(
                    description='<b>Name:</b>',
                    value='The name, a portion of the name, or a regular expression for the name of the desired item. '
                          'Enclose the text in "/" to use a regular expression. Example: /Area [ABC]_T.*/',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if 'Name' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Type:</b>',
                    value='Limit the search to specific item types. If "Any Type" is selected, then items of any '
                          'type included in the dropdown list will be included.',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if 'Type' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Asset Path:</b>',
                    value='The location in the asset tree to search below. Separate asset names with " >> ". '
                          'Example: "Example >> Cooling Tower 1 >> Area A".',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if 'Path' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Description:</b>',
                    value='Search within the description of an item.',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if 'Description' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Datasource:</b>',
                    value='Limit the search to specific datasources. You must be connected so Seeq when the widget is '
                          'created for the list to be populated.',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if
                    'Datasource Dropdown' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Datasource Name/ID/Class:</b>',
                    value='Limit the search to specific datasources by Name, ID, or Class. Some options may not be '
                          'available depending on configuration.',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if
                    'Datasource Name' in show_fields or
                    'Datasource ID' in show_fields or
                    'Datasource Class' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Workbook Scope:</b>',
                    value='Return only items that are scoped to a specific workbook using the workbook ID. '
                          'The workbook ID can be found in the URL after "workbook/".',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if 'Scoped To' in show_fields else ipywidgets.Layout(display='none')
                ),
                ipywidgets.HTML(
                    description='<b>Include Archived Items:</b>',
                    value='If checked, include items that have been archived.',
                    style={'description_width': 'initial'},
                    layout=ipywidgets.Layout() if 'Archived' in show_fields else ipywidgets.Layout(display='none')
                )
            ]
        )

        self._help_box = ipywidgets.Accordion(
            children=[self._help_text],
            selected_index=None,
            layout=ipywidgets.Layout(width='auto', grid_area='helpbox')
        )
        self._help_box.set_title(0, 'Help')
        if not show_help:
            self._help_box.layout.display = 'none'

        # Widget observer handles
        self._search_button.on_click(self._on_search_click)

        # Layout
        if 'Type' in show_fields:
            template_areas = '''
                        'helpbox helpbox helpbox'
                        'namebox namebox typebox'
                        'pathbox pathbox pathbox'
                        'descriptionbox descriptionbox descriptionbox'
                        'datasourcedropdown datasourcedropdown datasourcedropdown'
                        'datasourcenamebox datasourcenamebox datasourcenamebox'
                        'datasourceidbox datasourceidbox datasourceidbox'
                        'datasourceclassbox datasourceclassbox datasourceclassbox'
                        'scopedtobox scopedtobox scopedtobox'
                        'archivedbox archivedbox archivedbox'
                        'searchbutton searchbutton searchbutton'
                        'resultsbox resultsbox resultsbox'
                        '''
        else:
            template_areas = '''
                        'helpbox helpbox helpbox'
                        'namebox namebox namebox'
                        'pathbox pathbox pathbox'
                        'descriptionbox descriptionbox descriptionbox'
                        'datasourcedropdown datasourcedropdown datasourcedropdown'
                        'datasourcenamebox datasourcenamebox datasourcenamebox'
                        'datasourceidbox datasourceidbox datasourceidbox'
                        'datasourceclassbox datasourceclassbox datasourceclassbox'
                        'scopedtobox scopedtobox scopedtobox'
                        'archivedbox archivedbox archivedbox'
                        'searchbutton searchbutton searchbutton'
                        'resultsbox resultsbox resultsbox'
                        '''
        self._gb = ipywidgets.GridBox(
            children=[
                self._help_box,
                self._type_box,
                self._name_box,
                self._path_box,
                self._description_box,
                self._datasource_dropdown,
                self._datasource_name_box,
                self._datasource_id_box,
                self._datasource_class_box,
                self._archived_bool,
                self._scopedto_box,
                self._search_button,
                self._result_box,
            ],
            layout=ipywidgets.Layout(
                width='auto',
                grid_gap='0px 0px',
                grid_template_rows='auto auto',
                grid_template_columns='30% 40% 30%',
                grid_template_areas=template_areas
            )
        )

        super().__init__(
            children=[self.title, self._gb],
            layout=ipywidgets.Layout(width='auto'),
            **kwargs
        )

    @property
    def selected_value(self):
        return self._result_box.value

    @property
    def search_terms(self):
        return self._get_search_terms()

    @property
    def search_results(self):
        return self._found_seeq_items

    def _on_search_click(self, b):
        if self._session.client is None or not hasattr(self._session.client,
                                                       'auth_token') or not self._session.client.auth_token:
            self._result_box.options = ['You are not logged in to Seeq']
            self._result_box.disabled = True
            return
        self._result_box.disabled = True
        # _initializing_traites_ = True prevents selecting the first item in the list when setting a new options list
        # see github ipywidgets/ipywidgets/widgets/widget_selection._Selection._propagate_options
        self._result_box._initializing_traits_ = True
        self._result_box.options = [self._searching_seeq_text]
        search_terms = self._get_search_terms()
        self._search_seeq(search_terms)
        self._result_box.options = self._get_found_item_list()
        self._result_box.disabled = False
        self._result_box._initializing_traits_ = False

    def get_widget_state(self):
        """
        Get a dictionary of keywords and values that can be used as an argument on widget initialization to set a
        particular state. Selected items are not saved.

        Example
        -------
        >>> selector = SeeqItemSelect()
        >>> # modify the selector
        >>> selector_state = selector.get_widget_state()
        >>> # create a new selector with the same state as the last one
        >>> selector_2 = SeeqItemSelect(**selector_state)

        Returns
        -------
        dict
            A dictionary of the widget's state
        """

        state_dict = dict()
        if self.title.value:
            state_dict['title'] = self.title.value
        if self._name_box.value:
            state_dict['item_name'] = self._name_box.value
        state_dict['item_type'] = self._type_box.value
        if self._path_box.value:
            state_dict['item_path'] = self._path_box.value
        if self._description_box.value:
            state_dict['item_description'] = self._description_box.value
        if self._datasource_name_box.value:
            state_dict['item_datasource_name'] = self._datasource_name_box.value
        if self._datasource_id_box.value:
            state_dict['item_datasource_id'] = self._datasource_id_box.value
        if self._datasource_class_box.value:
            state_dict['item_datasource_class'] = self._datasource_class_box.value
        state_dict['item_archived'] = self._archived_bool.value
        if self._scopedto_box.value:
            state_dict['item_scoped_to'] = self._scopedto_box.value
        state_dict['show_fields'] = self._show_fields
        state_dict['type_options'] = self._seeq_item_types
        state_dict['datasource_dropdown'] = self._use_datasource_dropdown
        if self._use_datasource_dropdown:
            if self._datasource_dropdown.index != 0:
                idx = self._datasource_dropdown.index
                state_dict['item_datasource_name'] = self._datasource_dropdown.options[idx][0]
        state_dict['multi_select'] = self._use_multi_select
        state_dict['results_box_rows'] = self._result_box_rows
        state_dict['max_displayed_results'] = self._max_displayed_results
        state_dict['show_system_datasources'] = self._show_system_datasources
        state_dict['show_help'] = self._show_help
        if self._debug:
            state_dict['debug'] = True
        return state_dict

    def _get_found_item_list(self):
        # limit the display to the first 'limit' items
        if self._found_seeq_items is None:
            return []
        limit = self._max_displayed_results
        more_than_limit = len(self._found_seeq_items) > limit
        limit = limit if more_than_limit else len(self._found_seeq_items)
        item_list = list()
        for i in range(limit):
            item = self._found_seeq_items.iloc[i, :]
            if 'Path' not in item and 'Asset' not in item:
                location = ''
            elif isinstance(item['Path'], str) and isinstance(item['Asset'], str):
                location = f' on {item["Path"]} >> {item["Asset"]}'
            else:
                location = ''
            item_type = re.sub(r'(?<!^)(?=[A-Z])', ' ', item["Type"])
            item_list.append((f'{item["Name"]} ({item_type}{location})', item.to_dict()))
        if more_than_limit:
            item_list.append((f'... (Truncated at {limit} items)', None))
        return item_list

    def _get_search_terms(self):
        search_terms = dict()
        if self._name_box.value:
            search_terms['Name'] = self._name_box.value
        if self._type_box.value and (
                self._type_box.value in self._seeq_item_types or self._type_box.value == 'Any Type'):
            if self._type_box.value == 'Any Type':
                search_terms['Type'] = list(self._seeq_item_types) if isinstance(self._seeq_item_types, tuple) else \
                    self._seeq_item_types
            else:
                search_terms['Type'] = self._type_box.value
        if self._path_box.value:
            search_terms['Path'] = self._path_box.value
        if self._description_box.value:
            search_terms['Description'] = self._description_box.value
        if self._datasource_name_box.value and self._datasource_dropdown.value is None:
            search_terms['Datasource Name'] = self._datasource_name_box.value
        if self._datasource_id_box.value and self._datasource_dropdown.value is None:
            search_terms['Datasource ID'] = self._datasource_id_box.value
        if self._datasource_class_box.value and self._datasource_dropdown.value is None:
            search_terms['Datasource Class'] = self._datasource_class_box.value
        # Datasource Dropdown overrides the typed fields
        if self._datasource_dropdown.value is not None:
            if 'Datasource Name' in search_terms:
                del search_terms['Datasource Name']
            search_terms['Datasource Class'] = self._datasource_dropdown.value.datasource_class
            search_terms['Datasource ID'] = self._datasource_dropdown.value.datasource_id
        if self._scopedto_box.value:
            search_terms['Scoped To'] = self._scopedto_box.value
        search_terms['Archived'] = self._archived_bool.value
        return search_terms

    def _search_seeq(self, search_terms):
        if self._debug:
            print(f'Seeq Search Terms:\n{search_terms}')

        if not search_terms:
            self._found_seeq_items = None
        else:
            try:
                self._found_seeq_items = _search.search(search_terms, quiet=True)
            except RuntimeError as e:
                if 'No datasource found' in str(e):
                    self._found_seeq_items = None
                else:
                    raise
        if self._debug:
            print(f'Items returned from Seeq:\n{self._found_seeq_items}')


class LogWindowWidget(ipywidgets.VBox):
    def __init__(self, title):
        """
        An window for logging messages.

        See `SPy Documentation/spy.widgets.Log.ipynb` for usage.

        Parameters
        ----------
        title : str
            The title of the widget as an HTML string

        """
        self.handlers = list()
        _title_text = ipywidgets.HTML(
            value=title,
            layout=ipywidgets.Layout(width='auto')
        )

        self.level_select = ipywidgets.Dropdown(
            description='Display Log Level: ',
            options=[('Debug', logging.DEBUG), ('Info', logging.INFO),
                     ('Warning', logging.WARNING), ('Error', logging.ERROR), ('Critical', logging.CRITICAL)],
            layout=ipywidgets.Layout(width='auto', height='auto', margin='0px 0px 0px 10px'),
            style={'description_width': 'initial'}
        )

        _title_box = ipywidgets.HBox(
            children=[_title_text, self.level_select],
            layout=ipywidgets.Layout(width='100%', align_items='center')
        )

        self.message_window = ipywidgets.Textarea(
            rows=4,
            disabled=True,
            layout=ipywidgets.Layout(width='auto')
        )

        # events
        self.level_select.observe(self._on_level_change, names='value')

        super().__init__(
            children=[
                ipywidgets.HTML("<style>.opacity-full textarea:disabled { opacity: 100% !important; }</style>"),
                _title_box,
                self.message_window]
        )
        self.message_window.add_class('opacity-full')

    @property
    def log_level_options(self):
        return self.level_select.options

    @log_level_options.setter
    def log_level_options(self, value):
        self.level_select.options = value

    @property
    def log_level(self):
        return self.level_select.value

    def _on_level_change(self, change):
        if not isinstance(self.handlers, (list, tuple)):
            self.handlers = [self.handlers]
        for h in self.handlers:
            # noinspection PyUnresolvedReferences
            h.setLevel(change['new'])
