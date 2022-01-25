import glob
import json
import os
import re
from typing import Optional

import pandas as pd
from deprecated import deprecated
from mako.template import Template
from mako.lookup import TemplateLookup

from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq import spy
from seeq.spy.workbooks._item import Item
from seeq.spy.workbooks._workstep import Workstep, AnalysisWorkstep, ExistingWorkstepWalk
from seeq.spy.workbooks._annotation import Journal, Report
from seeq.spy.workbooks._content import DateRange
from seeq.spy import _common
from seeq.spy import _url
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks._annotation import Journal, Report
from seeq.spy.workbooks._content import DateRange
from seeq.spy.workbooks._item import Item
from seeq.spy.workbooks._workstep import Workstep, AnalysisWorkstep, ExistingWorkstepWalk


class Worksheet(Item):
    def __new__(cls, *args, **kwargs):
        if cls is Worksheet:
            raise SPyTypeError("Worksheet may not be instantiated directly, create either AnalysisWorksheet or "
                               "TopicWorksheet")

        return object.__new__(cls)

    def __init__(self, workbook, definition=None):
        super().__init__(definition)

        if workbook is None:
            raise SPyValueError("A Workbook is required to create a Worksheet")

        self.workbook = workbook
        self.workbook.worksheets.append(self)

        if self.workbook['Workbook Type'] == 'Analysis':
            self.document = Journal(self)
            self.worksteps = dict()
            workstep = AnalysisWorkstep(self)
            self.definition['Current Workstep ID'] = workstep['ID']
        else:
            self.document = Report(self)

    @property
    def url(self):
        """
        The URL of the worksheet.

        Note that value won't be filled if the workbook/worksheet hasn't been pulled from Seeq.

        Returns
        -------
        str
            The worksheet's URL
        """
        # Note that 'URL' won't be filled in if a workbook/worksheet hasn't been pushed/pulled. That's because the
        # IDs may change from the placeholders that get generated.
        return self['URL']

    @staticmethod
    def _instantiate(workbook, definition=None):
        if workbook['Workbook Type'] == 'Analysis':
            return AnalysisWorksheet(workbook, definition)
        else:
            return TopicDocument(workbook, definition)

    @staticmethod
    def pull(item_id, *, workbook=None, extra_workstep_tuples=None, include_images=True,
             session: Optional[Session] = None):
        session = Session.validate(session)
        if workbook is None:
            raise SPyValueError('workbook argument is None -- must be a valid Workbook object')

        try:
            definition = Item._dict_from_item_output(Item._get_item_output(session, item_id))
        except ApiException:
            raise SPyRuntimeError(f'Worksheet with ID "{item_id}" does not exist')
        worksheet = Worksheet._instantiate(workbook, definition)
        worksheet.pull_worksheet(session, item_id, extra_workstep_tuples=extra_workstep_tuples,
                                 include_images=include_images)
        return worksheet

    def pull_worksheet(self, session: Session, worksheet_id, extra_workstep_tuples=None, include_images=True):
        self.provenance = Item.PULL

        self.document.pull(session, include_images=include_images)

        link_url = _url.SeeqURL.parse(session.public_url)
        link_url.route = _url.Route.WORKBOOK_EDIT
        link_url.folder_id = self.workbook['Ancestors'][-1] if len(self.workbook['Ancestors']) > 0 else None
        link_url.workbook_id = self.workbook.id
        link_url.worksheet_id = self.id
        self['URL'] = link_url.url

    def pull_rendered_content(self, session: Session, *, errors='raise', quiet=False, status: Status = None):
        pass

    def item_map_worksteps_key(self):
        return f'Worksteps for {self.id}'

    def push(self, session: Session, pushed_workbook_id, item_map, datasource_output, existing_worksheet_identifiers,
             include_inventory, label=None, item_push_errors=None):
        existing_worksheet_id = None

        data_id = self._construct_data_id(label)

        # After Integrated Security was introduced, we can no longer search for Worksheets using Data ID,
        # so we use the passed-in dictionary that the Workbook assembled to find existing worksheets.
        if self.id in existing_worksheet_identifiers:
            existing_worksheet_id = existing_worksheet_identifiers[self.id]
        elif data_id in existing_worksheet_identifiers:
            existing_worksheet_id = existing_worksheet_identifiers[data_id]
        elif self.provenance == Item.CONSTRUCTOR and self.name in existing_worksheet_identifiers:
            existing_worksheet_id = existing_worksheet_identifiers[self.name]

        workbooks_api = WorkbooksApi(session.client)
        items_api = ItemsApi(session.client)
        props = list()
        if not existing_worksheet_id:
            worksheet_input = WorksheetInputV1()
            worksheet_input.name = self.definition['Name']
            worksheet_output = workbooks_api.create_worksheet(
                workbook_id=pushed_workbook_id, body=worksheet_input)  # type: WorksheetOutputV1

            props = [ScalarPropertyV1(name='Datasource Class', value=datasource_output.datasource_class),
                     ScalarPropertyV1(name='Datasource ID', value=datasource_output.datasource_id),
                     ScalarPropertyV1(name='Data ID', value=data_id)]
        else:
            worksheet_output = workbooks_api.get_worksheet(workbook_id=pushed_workbook_id,
                                                           worksheet_id=existing_worksheet_id)
            props.append(ScalarPropertyV1(name='Name', value=self.definition['Name']))

        item_map[self.id.upper()] = worksheet_output.id.upper()

        props.append(ScalarPropertyV1(name='Archived', value=_common.get(self, 'Archived', False)))
        items_api.set_properties(id=worksheet_output.id, body=props)

        return worksheet_output

    @property
    def referenced_items(self):
        referenced_items = list()
        if hasattr(self, 'worksteps'):
            for workstep_id, workstep in self.worksteps.items():  # type: Workstep
                referenced_items.extend(workstep.referenced_items)

        referenced_items.extend(self.document.referenced_items)

        return referenced_items

    @property
    def referenced_worksteps(self):
        return self.document.referenced_worksteps

    def find_workbook_links(self, session: Session):
        return self.document.find_workbook_links(session)

    def push_fixed_up_workbook_links(self, session: Session, item_map, label, datasource_output):
        if self.workbook.id not in item_map or self.id not in item_map:
            return

        self.document.push(session, item_map[self.workbook.id], item_map[self.id], item_map, datasource_output,
                           push_images=False, label=label, item_push_errors=None)

    def current_workstep(self) -> AnalysisWorkstep:
        return self.worksteps[self.definition['Current Workstep ID']]

    @staticmethod
    def _get_worksheet_json_file(workbook_folder, worksheet_id):
        return os.path.join(workbook_folder, 'Worksheet_%s.json' % worksheet_id)

    def save(self, workbook_folder, *, include_rendered_content=False, pretty_print_html=False):
        worksheet_json_file = Worksheet._get_worksheet_json_file(workbook_folder, self.id)

        with open(worksheet_json_file, 'w', encoding='utf-8') as f:
            json.dump(self.definition, f, indent=4)

        self.document.save(workbook_folder, include_rendered_content=include_rendered_content,
                           pretty_print_html=pretty_print_html)

    def _load(self, workbook_folder, worksheet_id):
        worksheet_json_file = Worksheet._get_worksheet_json_file(workbook_folder, worksheet_id)

        with open(worksheet_json_file, 'r', encoding='utf-8') as f:
            self.definition = json.load(f)

        self.provenance = Item.LOAD

        if self.workbook['Workbook Type'] == 'Analysis':
            self.document = Journal.load(self, workbook_folder)
        else:
            self.document = Report.load(self, workbook_folder)

        self.worksteps = dict()
        workstep_files = glob.glob(os.path.join(workbook_folder, 'Worksheet_%s_Workstep_*.json' % worksheet_id))
        for workstep_file in workstep_files:
            match = re.match(r'.*?Worksheet_.*?_Workstep_(.*?).json$', workstep_file)
            workstep_id = match.group(1)
            self.worksteps[workstep_id] = Workstep.load_from_workbook_folder(self, workbook_folder, workstep_id)

    @staticmethod
    def load_from_workbook_folder(workbook, workbook_folder, worksheet_id):
        worksheet = Worksheet._instantiate(workbook)
        worksheet._load(workbook_folder, worksheet_id)
        return worksheet

    @property
    def timezone(self):
        """
        The timezone for the worksheeet

        Returns
        -------
        {str, None}
            The string name of the worksheet's current timezone or None
            if one is not set
        """
        return self._get_timezone()

    @timezone.setter
    def timezone(self, value):
        self._set_timezone(value)

    def _set_timezone(self, timezone):
        # type: (str) -> None
        """
        Set the timezone for the current worksheet.

        A list of all timezone names is available in the pytz module:
        All timezones
            pytz.all_timezones
        Those for a specific country
            pytz.country_timezones('US')
            Where the abbreviations for countries can be found from
            list(pytz.country_names.items())

        Parameters
        ----------
        timezone : str
            The name of the desired timezone
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.timezone = timezone

    def _get_timezone(self) -> Optional[str]:
        """
        Get the timezone name.

        See property "timezone"

        Returns
        -------
        {str, None}
            The string name of the worksheet's current timezone or None
            if one is not set
        """
        return self.current_workstep().timezone

    def _branch_current_workstep(self):
        if self.provenance == self.CONSTRUCTOR:
            return self.current_workstep()

        if 'Current Workstep ID' in self.definition and self.definition['Current Workstep ID']:
            new_workstep = AnalysisWorkstep(self,
                                            definition={
                                                'Data': self.worksteps[self.definition['Current Workstep ID']].data})
        else:
            new_workstep = AnalysisWorkstep(self)

        self.worksteps[new_workstep['ID']] = new_workstep
        self.definition['Current Workstep ID'] = new_workstep['ID']

        return new_workstep

    def remove_workstep(self, workstep):
        if workstep.id in self.worksteps:
            del self.worksteps[workstep.id]


class AnalysisWorksheet(Worksheet):
    def workstep(self, name=None, create=True):
        if not name:
            name = _common.new_placeholder_guid()

        existing_workstep = [ws for ws in self.worksteps.values() if ws.name == name]
        if len(existing_workstep) == 1:
            return existing_workstep[0]
        elif not create:
            return None

        workstep = AnalysisWorkstep(self, {'Name': name})
        workstep.set_as_current()

        return workstep

    def pull_worksheet(self, session: Session, worksheet_id, extra_workstep_tuples=None, include_images=True):
        super().pull_worksheet(session, worksheet_id)

        workbooks_api = WorkbooksApi(session.client)
        worksheet_output = workbooks_api.get_worksheet(
            workbook_id=self.workbook.id, worksheet_id=worksheet_id)  # type: WorksheetOutputV1
        current_workstep_id = Workstep.parse_workstep_id(worksheet_output.workstep)

        workstep_tuples_to_pull = set()
        if current_workstep_id is not None:
            workstep_tuples_to_pull.add((self.workbook.id, self.id, current_workstep_id))
            self.definition['Current Workstep ID'] = current_workstep_id

        for workbook_id, worksheet_id, workstep_id in self.document.referenced_worksteps:
            if isinstance(self.document, Journal) or worksheet_id == self.id:
                workstep_tuples_to_pull.add((workbook_id, worksheet_id, workstep_id))

        if extra_workstep_tuples:
            for workbook_id, worksheet_id, workstep_id in extra_workstep_tuples:
                if workbook_id == self.workbook.id and worksheet_id == self.id and workstep_id is not None:
                    workstep_tuples_to_pull.add((workbook_id, worksheet_id, workstep_id))
        self._pull_worksteps(session, workstep_tuples_to_pull)

        if not self.worksteps:
            workstep = AnalysisWorkstep(self)
            self.definition['Current Workstep ID'] = workstep['ID']

    def _pull_worksteps(self, session: Session, workstep_tuples):
        for workstep_tuple in workstep_tuples:
            workbook_id, worksheet_id, workstep_id = workstep_tuple
            if workstep_id not in self.worksteps:
                self.workbook.update_status('Pulling worksteps', 0)
                self.worksteps[workstep_id] = Workstep.pull(workstep_tuple, worksheet=self, session=session)
                self.workbook.update_status('Pulling worksteps', 1)

    def push(self, session: Session, pushed_workbook_id, item_map, datasource_output, existing_worksheet_identifiers,
             include_inventory, label=None, item_push_errors=None):
        worksheet_output = super().push(session, pushed_workbook_id, item_map, datasource_output,
                                        existing_worksheet_identifiers, include_inventory, label=label,
                                        item_push_errors=item_push_errors)

        existing_workstep_walk = ExistingWorkstepWalk(pushed_workbook_id, worksheet_output)

        pushed_current_workstep_id = None
        for workstep_id, workstep in self.worksteps.items():  # type: (str, Workstep)
            self.workbook.update_status('Pushing worksteps', 0)
            # Intentionally don't send a workstep message since it will be sent below when we set the current workstep
            pushed_workstep_id = workstep.push_to_specific_worksheet(session, pushed_workbook_id, worksheet_output,
                                                                     item_map, include_inventory,
                                                                     existing_workstep_walk=existing_workstep_walk,
                                                                     no_workstep_message=True)
            self.workbook.update_status('Pushing worksteps', 1)

            # We have to store off a per-worksheet map of worksteps because of the way they can be duplicated due
            # to duplicated worksheets and copy/pasted Journal links
            if self.item_map_worksteps_key() not in item_map:
                item_map[self.item_map_worksteps_key()] = dict()
            item_map[self.item_map_worksteps_key()][workstep_id.upper()] = pushed_workstep_id.upper()

            if workstep_id == self.definition['Current Workstep ID']:
                pushed_current_workstep_id = pushed_workstep_id

        if not pushed_current_workstep_id:
            raise SPyRuntimeError("Workstep for worksheet's 'Current Workstep ID' not found")

        workbooks_api = WorkbooksApi(session.client)
        # We have to do this at the end otherwise the other pushed worksheets will take precedence
        workbooks_api.set_current_workstep(workbook_id=pushed_workbook_id,
                                           worksheet_id=worksheet_output.id,
                                           workstep_id=pushed_current_workstep_id)

        self.document.push(session, pushed_workbook_id, worksheet_output.id, item_map, datasource_output,
                           push_images=True, label=label, item_push_errors=item_push_errors)

        return worksheet_output

    def refresh_from(self, new_item, item_map):
        super().refresh_from(new_item, item_map)

        self.document.refresh_from(new_item.document, item_map)

        # Worksteps are always pushed fresh, so there's no mapping from old worksteps to new ones. As a result,
        # if the user is holding on to a Workstep object, it won't be refreshed. (We don't expect that users will do
        # that.)
        self.worksteps = new_item.worksteps

    def save(self, workbook_folder, *, include_rendered_content=False, pretty_print_html=False):
        super().save(workbook_folder, include_rendered_content=include_rendered_content,
                     pretty_print_html=pretty_print_html)

        for workstep_id, workstep in self.worksteps.items():
            workstep.save(workbook_folder)

    @property
    def display_items(self):
        """
        Add items to the display pane.

        Items in the input data frame that do not have a known store will be
        skipped.

        Parameters
        ----------
        dict, pd.DataFrame, pd.Series
            A pandas DataFrame with the items to be added to the display. It
            must minimally have 'ID' and 'Type' columns. Display attributes
            should be in named columns as described below.

            Type Key:
            Si = Signal, Sc = Scalar, C = Condition, M = Metric, T = Table

            ================= =================================== =============
            Display Attribute Description                         Applicability
            ================= =================================== =============
            Color             A 3-part RGB hexadecimal color spec
                              starting with "#".  E.g. #CE561B    All
            Axis Auto Scale   Boolean if the axis should auto
                              scale                               Si, Sc, M
            Axis Limits       A dict of {'min': float,
                              'max': float} to specify the axis
                              limits. Ignored if Auto Axis Scale
                              is True.                            Si, Sc, M
            Axis Group        An identifier to specify shared
                              axes                                Si, Sc, M
            Lane              The lane a trend is plotted in      Si, Sc, M
            Align             Specify the side of the plot for
                              the y-axis. 'Left' (default) or
                              'Right'.                            Si, Sc, M
            Line              The trend line style. Options are
                              ['Solid', 'Dot', 'Short Dash',
                               'Long Dash', 'Short Dash-Dot',
                               'Short Dash-Dot-Dot',
                               'Long Dash-Dot',
                               'Long Dash-Dot-Dot', 'Dash-Dot']   Si, Sc, M
            Line Width        The width of the line.              Si, Sc, M
            Samples           The sample display style. Options
                              are ['Line', 'Line and Sample',
                               'Samples', 'Bars']                 Si
            Stack             Boolean indicating if bars should
                              be stacked                          T

        Returns
        -------
        pd.DataFrame
            A DataFrame with all items displayed on the worksheet, including display
            settings.
        """
        return self._get_display_items()

    @display_items.setter
    def display_items(self, value):
        self._set_display_items(items_df=value)

    @property
    def view(self):
        """
        Set the view of the workstep.

        Parameters
        ----------
        str or None
            The desired view for the workstep. Valid values are

            ============ =========================================
            View         Result
            ============ =========================================
            Trend        Show the time-series trend view (default)
            Scatter Plot Show the scatter plot view
            Treemap      Show the treemap view
            Scorecard    Show the table view
            Table        Show the table view
            ============ =========================================

        Returns
        -------
        str or None
            The current view of the worksheet or None if not set
        """
        return self._get_worksheet_view()

    @view.setter
    def view(self, value):
        self._set_worksheet_view(value)

    @property
    def display_range(self):
        """
        Set the display range on the worksheet

        Parameters
        ----------
        pandas.DataFrame, pandas.Series, dict
            The display range as a single row DataFrame, Series or dict with
            columns of 'Start' and 'End' containing the datetime objects or
            text parsable using pandas.to_datetime().

        Returns
        -------
         dict
            A dict with keys of 'Start' and 'End' and values of the ISO8601
            timestamps for the start and end of the display range.
        """
        return self._get_display_range()

    @display_range.setter
    def display_range(self, value):
        self._set_display_range(value)

    @property
    def investigate_range(self):
        """
        Set the investigate range on the worksheet

        Parameters
        ----------
        pandas.DataFrame, pandas.Series, dict
            The investigate range as a single row DataFrame, Series or dict
            with columns of 'Start' and 'End' containing the datetime objects
            or text parsable using pandas.to_datetime().

        Returns
        -------
        dict
            A dict with keys of 'Start' and 'End' and values of the ISO8601
            timestamps for the start and end of the investigate range.
        """
        return self._get_investigate_range()

    @investigate_range.setter
    def investigate_range(self, value):
        self._set_investigate_range(value)

    @property
    @deprecated(reason='Use self.table_date_display instead')
    def scorecard_date_display(self):
        return self.table_date_display

    @scorecard_date_display.setter
    @deprecated(reason='Use self.table_date_display instead')
    def scorecard_date_display(self, value):
        self.table_date_display = value

    @property
    @deprecated(reason='Use self.table_date_format instead')
    def scorecard_date_format(self):
        return self.table_date_format

    @scorecard_date_format.setter
    @deprecated(reason='Use self.table_date_format instead')
    def scorecard_date_format(self, value):
        self.table_date_format = value

    @property
    def table_date_display(self):
        """
        Get/Set the date display for tables

        Parameters
        ----------
        str or None
            The dates that should be displayed for tables.
            Valid values are:

            =============== ================================
            Date Display    Result
            =============== ================================
            None            No date display
            'Start'         Start of the time period only
            'End'           End of the time period only
            'Start And End' Start and end of the time period
            =============== ================================

        Returns
        -------
        str or None
            The table date display
        """
        return self._get_table_date_display()

    @table_date_display.setter
    def table_date_display(self, value):
        self._set_table_date_display(value)

    @property
    def table_date_format(self):
        """
        Get/Set the format for table date displays

        Parameters
        ----------
        str or None
            The string defining the date format. Formats are parsed using
            momentjs. The full documentation for the momentjs date parsing
            can be found at https://momentjs.com/docs/#/displaying/

        Examples
        --------
        "d/m/yyy" omitting leading zeros (eg, 4/27/2020): l
        "Mmm dd, yyyy, H:MM AM/PM" (eg, Apr 27, 2020 5:00 PM) : lll
        "H:MM AM/PM" (eg, "5:00 PM"): LT

        Returns
        -------
        str
            The formatting string
        """
        return self._get_table_date_format()

    @table_date_format.setter
    def table_date_format(self, value):
        self._set_table_date_format(value)

    @property
    def table_mode(self):
        """
        Get/Set the current Table view mode

        Parameters
        ----------
        str or None
            The string defining the Table view mode. Can be either "simple"
            or "condition".

        Returns
        -------
        str
            The Table view mode
        """
        return self._get_table_mode()

    @table_mode.setter
    def table_mode(self, value):
        self._set_table_mode(value)

    @property
    def scatter_plot_series(self):
        # noinspection PyUnresolvedReferences
        """
        Get/Set the IDs of the item plotted on the x-axis of a scatter plot

        Parameters
        ----------
        dict or None
            A dict with keys of the axis name (either 'X' or 'Y') and values of
            dicts, Series, or one-row DataFrames with a column of 'ID' for the
            item to use for the axis.

        Returns
        -------
        dict or None
            A dict with keys of 'X' and 'Y' and values of dicts with a key of
            'ID' and a value of either the Seeq ID of the item or None if not
            specified. Returns None if neither is specified

        Example
        -------
        >>> series = worksheet.scatter_plot_series
        >>> print(series)
            {
                'X': {'ID': '57ADF442-C571-4B19-B358-E03D77CE68B4'},
                'Y': {'ID': '3E4571C8-66C0-428E-8B04-FE0FB9F140BB'}
            }
        """
        return self._get_scatter_plot_series()

    @scatter_plot_series.setter
    def scatter_plot_series(self, value):
        self._set_scatter_plot_series(value)

    def _get_display_range(self) -> Optional[dict]:
        """
        Get the display range for the workstep

        See worksheet property "display_range" for docs

        :return:
        """
        return self.current_workstep().display_range

    def _set_display_range(self, display_range: dict):
        new_workstep = self._branch_current_workstep()
        new_workstep.display_range = display_range

    def _get_investigate_range(self) -> Optional[dict]:
        """
        Get the investigate range of the current workstep

        See worksheet property "investigate_range" for docs
        """
        return self.current_workstep().investigate_range

    def _set_investigate_range(self, investigate_range: dict):
        new_workstep = self._branch_current_workstep()
        new_workstep.investigate_range = investigate_range

    def _get_display_items(self) -> Optional[pd.DataFrame]:
        """
        Get the items of a given type displayed on the worksheet at the current workstep, regardless of the worksheet
        view

        Returns
        -------
        {pandas.DataFrame None}
            A list of the items present on the worksheet at the current workstep, or None if there is no current
            workstep ID or the current workstep has no data
        """
        return self.current_workstep().display_items

    def _set_display_items(self, items_df: pd.DataFrame):
        """
        Get the display items

        See worksheet property "display items" for docs
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.display_items = items_df

    def _set_worksheet_view(self, view_key='Trend'):
        """
        Set the view key

        See worksheet property "view"
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.view = view_key

    def _get_worksheet_view(self):
        return self.current_workstep().view

    def _set_table_date_display(self, date_display):
        """
        Set the date display

        See worksheet property "table_date_display" for docs
        :param date_display:
        :return:
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.table_date_display = date_display

    def _get_table_date_display(self):
        return self.current_workstep().table_date_display

    def _set_table_date_format(self, date_format):
        """
        Set the table date format

        See worksheet property "table_date_format" for docs
        :param date_format:
        :return:
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.table_date_format = date_format

    def _get_table_date_format(self):
        return self.current_workstep().table_date_format

    def _set_table_mode(self, mode):
        """
        Set the Table view mode

        See worksheet property "table_mode" for docs
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.table_mode = mode

    def _get_table_mode(self):
        return self.current_workstep().table_mode

    def _set_scatter_plot_series(self, series_ids):
        """
        Set the IDs of the series to use for the axes of scatter plots

        Parameters
        ----------
        series_ids : dict
            A dict with keys of the axis name (either 'X' or 'Y') and values of
            the Seeq IDs of the items.
        """
        new_workstep = self._branch_current_workstep()
        new_workstep.scatter_plot_series = series_ids

    def _get_scatter_plot_series(self):
        return self.current_workstep().scatter_plot_series

    @staticmethod
    def add_display_columns(df, inplace=True):
        """
        Add the display attribute columns to a pandas.DataFrame

        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame that will have the columns added

        inplace : boolean, default True
            If True, the columns of the DataFrame passed in will be modified and
            None will be returned. If False a copy of df with the new columns
            will be returned

        Returns
        -------
        {None, pandas.DataFrame}
            None if inplace == True. A pandas.DataFrame deep copy with the
            display attribute columns added if inplace == False
        """
        return AnalysisWorkstep.add_display_columns(df, inplace)


class TopicDocument(Worksheet):
    def pull_rendered_content(self, session: Session, *, errors='raise', quiet=False, status: Status = None):
        status = Status.validate(status, quiet)

        if self.document:
            self.document.pull_rendered_content(session, errors=errors, quiet=quiet, status=status)

    def push(self, session: Session, pushed_workbook_id, item_map, datasource_output, existing_worksheet_identifiers,
             include_inventory, label=None, item_push_errors=None):
        worksheet_output = super().push(session, pushed_workbook_id, item_map, datasource_output,
                                        existing_worksheet_identifiers, include_inventory, label=label,
                                        item_push_errors=item_push_errors)

        self.document.push(session, pushed_workbook_id, worksheet_output.id, item_map, datasource_output,
                           push_images=True, label=label, item_push_errors=item_push_errors)

        return worksheet_output

    def refresh_from(self, new_item, item_map):
        super().refresh_from(new_item, item_map)

        self.document.refresh_from(new_item.document, item_map)

    def render_template(self, text=None, filename=None, **kwargs):
        if filename:
            sibling_folder_lookup = TemplateLookup(directories=[os.path.dirname(filename)])
            template = Template(filename=filename, lookup=sibling_folder_lookup, input_encoding='utf-8')
        elif text:
            template = Template(text=text)
        else:
            raise SPyValueError('Either html or filename must be supplied')

        def _display(display, date_range=None, *, size='medium', shape='rectangle', width=None, height=None,
                     scale=1.0, selector=''):
            if not isinstance(display, AnalysisWorkstep):
                raise SPyValueError(
                    f'The first argument you gave display() is "{display}", of type "{type(date_range)}" - '
                    f'check your @Asset.Display function. It needs to be decorated with @Asset.Display '
                    f'and return a valid AnalysisWorkstep.')

            if not isinstance(date_range, DateRange) and date_range is not None:
                raise SPyValueError(f'The date_range specified is "{date_range}", of type "{type(date_range)}" - check '
                                    f'the date range definition in your Asset class function, it needs to be decorated '
                                    f'with @Asset.DateRange and return a valid date range')

            return self.document.get_embedded_content_html(display, date_range, size=size, shape=shape, width=width,
                                                           height=height, scale=scale,
                                                           selector=selector)

        def _plot(plot_function, date_range):
            return self.document.add_plot_to_render(plot_function, date_range)

        folder_for_relative_paths = os.path.dirname(filename)

        # noinspection PyShadowingNames
        def _image(filename=None, *, buffer=None, image_format=None):
            if not os.path.isabs(filename):
                filename = os.path.join(folder_for_relative_paths, filename)
            return self.document.add_image(filename=filename, buffer=buffer, image_format=image_format, just_src=True)

        kwargs['display'] = _display
        kwargs['plot'] = _plot
        kwargs['image'] = _image

        self.html = template.render(**kwargs)

    @property
    def html(self):
        """
        Get/Set the raw HTML for the topic document

        Parameters
        ----------
        str or None
            An HTML string to display in the document

        Returns
        -------
        str
            The current HTML string for the document
        """
        return self.document.html

    @html.setter
    def html(self, value):
        self.document.html = value

    @property
    def date_ranges(self):
        return self.document.date_ranges

    @property
    def content(self):
        return self.document.content

    @property
    def schedule(self):
        # noinspection PyUnresolvedReferences, HttpUrlsUsage
        """
                Get/Set the schedule for the topic document. The schedule determines whether a document is a live,
                auto-updating document or a scheduled document.

                Parameters
                ----------
                dict or None
                    A dictionary of a 'Background' and a 'Cron Schedule' for document's schedule

                        ===================== =============================================
                        Input Column          Schedule Attribute
                        ===================== =============================================
                        Background            Whether the document is scheduled or live
                        Cron Schedule         The document's update schedule as a cron
                                              schedule. This should be a list of cron
                                              expressions such as ['0 */5 * * * ?']. See
                                              http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
                                              for more information

                Returns
                -------
                dict
                    The current dictionary containing the 'Background' variable and 'Cron Schedule' for the document's schedule
        """
        return self.document.schedule

    @schedule.setter
    def schedule(self, value):
        self.document.schedule = value


def get_analysis_worksheet_from_url(url, include_archived=False, quiet=False):
    """
    Get a worksheet from a valid Workbench Analysis URL.

    Parameters
    ----------
    url : str
        The URL of the Workbench Analysis
    include_archived : bool, default False
        If True, returns the worksheet even if the workbook is archived. If False, raises an exception
        if the workbook is archived.
    quiet : bool, default False
        If True, suppresses progress output.

    Returns
    -------
    {Worksheet}
        The Worksheet object
    """
    workbook_id = _url.get_workbook_id_from_url(url)
    worksheet_id = _url.get_worksheet_id_from_url(url)

    if workbook_id is None or worksheet_id is None:
        raise SPyValueError(f'The supplied URL is not a valid Seeq address. Verify that both the workbook ID and '
                            f'worksheet ID are valid Seeq references')

    workbook_search = spy.workbooks.search({'ID': workbook_id}, quiet=quiet)
    if len(workbook_search) == 0:
        raise SPyRuntimeError(f'Could not find workbook with ID "{workbook_id}"')
    workbook = spy.workbooks.pull(workbook_search, include_referenced_workbooks=False, include_inventory=False,
                                  specific_worksheet_ids=[worksheet_id], quiet=quiet)[0]

    if _common.get(workbook.definition, 'Archived') and not include_archived:
        raise SPyValueError(f"Workbook '{workbook_id}' is archived. Supply 'include_archive=True' if"
                            f"you want to retrieve the items of an archived workbook")

    if workbook.definition['Workbook Type'] != 'Analysis':
        raise SPyValueError(f'URL must be for a valid Workbench Analysis. '
                            f'You supplied a URL for a {workbook.definition["Workbook Type"]}.')

    try:
        worksheet = [x for x in workbook.worksheets if x.id == worksheet_id][0]
        if _common.get(worksheet.definition, 'Archived') and not include_archived:
            raise SPyValueError(f"Worksheet '{worksheet_id}' is archived. Supply 'include_archive=True' if"
                                f"you want to retrieve archived items")
        return worksheet
    except IndexError:
        raise SPyRuntimeError(f'Worksheet with ID "{worksheet_id}" does not exist in workbook "{workbook.name}"')
