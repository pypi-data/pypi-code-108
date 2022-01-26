import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse, ParseResult

from seeq.spy import _common
from seeq.spy._errors import *


class HttpProtocol(Enum):
    HTTP = 1
    HTTPS = 2


class Route(Enum):
    HOME = 1
    WORKBOOK_EDIT = 2
    WORKBOOK_VIEW = 3
    WORKBOOK_PRESENTATION = 4
    JOURNAL_WORKSTEP_LINK = 5
    DATALAB_PROJECT = 6
    UNKNOWN = 7


@dataclass
class SeeqURL:
    protocol: HttpProtocol
    hostname: str
    port: int
    route: Route
    _folder_id: str
    _workbook_id: str
    _worksheet_id: str
    _workstep_id: str
    _datalab_project_id: str

    def __init__(self, *, protocol=None, hostname=None, port=None, route=None, folder_id=None, workbook_id=None,
                 worksheet_id=None, workstep_id=None, datalab_project_id=None):
        self.protocol = protocol
        self.hostname = hostname
        self.port = port
        self.route = route
        self.folder_id = folder_id
        self.workbook_id = workbook_id
        self.worksheet_id = worksheet_id
        self.workstep_id = workstep_id
        self.datalab_project_id = datalab_project_id

    @property
    def folder_id(self):
        return self._folder_id

    @folder_id.setter
    def folder_id(self, val):
        self._folder_id = None if val is None else val.upper()

    @property
    def workbook_id(self):
        return self._workbook_id

    @workbook_id.setter
    def workbook_id(self, val):
        self._workbook_id = None if val is None else val.upper()

    @property
    def worksheet_id(self):
        return self._worksheet_id

    @worksheet_id.setter
    def worksheet_id(self, val):
        self._worksheet_id = None if val is None else val.upper()

    @property
    def workstep_id(self):
        return self._workstep_id

    @workstep_id.setter
    def workstep_id(self, val):
        self._workstep_id = None if val is None else val.upper()

    @property
    def datalab_project_id(self):
        return self._datalab_project_id

    @datalab_project_id.setter
    def datalab_project_id(self, val):
        self._datalab_project_id = None if val is None else val.upper()

    @property
    def address(self):
        address = f"{'http' if self.protocol == HttpProtocol.HTTP else 'https'}://{self.hostname}"
        if (self.protocol == HttpProtocol.HTTP and self.port != 80) or \
                (self.protocol == HttpProtocol.HTTPS and self.port != 443):
            address += f':{self.port}'
        return address

    @property
    def path(self):
        if self.route == Route.WORKBOOK_EDIT:
            if self.folder_id is not None:
                return f'/{self.folder_id}/workbook/{self.workbook_id}/worksheet/{self.worksheet_id}'
            else:
                return f'/workbook/{self.workbook_id}/worksheet/{self.worksheet_id}'
        elif self.route == Route.WORKBOOK_VIEW:
            return f'/view/{self.worksheet_id}'
        elif self.route == Route.WORKBOOK_PRESENTATION:
            return f'/present/worksheet/{self.workbook_id}/{self.worksheet_id}'
        elif self.route == Route.JOURNAL_WORKSTEP_LINK:
            return f'/links'
        elif self.route == Route.HOME:
            if self.folder_id is not None:
                return f'/{self.folder_id}/folder/'
            else:
                return f'/workbooks'
        elif self.route == Route.DATALAB_PROJECT:
            return f'/data-lab/{self.datalab_project_id}'

        return ''

    @property
    def parameters(self):
        if self.route == Route.WORKBOOK_VIEW:
            if self.workstep_id is not None:
                return f'?workstepId={self.workstep_id}'
        elif self.route == Route.JOURNAL_WORKSTEP_LINK:
            return f'?type=workstep&workbook={self.workbook_id}' \
                   f'&worksheet={self.worksheet_id}&workstep={self.workstep_id}'

        return ''

    @property
    def url(self):
        return f'{self.address}{self.path}{self.parameters}'

    ADDRESS_REGEX = re.compile(r'^(?P<protocol>https?)://(?P<hostname>[^:/?]+)(?::(?P<port>\d+))?', re.IGNORECASE)

    ROUTES = {
        Route.WORKBOOK_EDIT: (re.compile(rf'^(?:/(?P<folder_id>{_common.GUID_REGEX}))?'
                                         rf'/workbook/(?P<workbook_id>{_common.GUID_REGEX})'
                                         rf'/worksheet/(?P<worksheet_id>{_common.GUID_REGEX})', re.IGNORECASE),
                              dict()),
        Route.WORKBOOK_VIEW: (re.compile(rf'^/view/(?P<worksheet_id>{_common.GUID_REGEX})', re.IGNORECASE),
                              {'workstepId': 'workstep_id'}),
        Route.WORKBOOK_PRESENTATION: (re.compile(rf'^/present/worksheet/(?P<workbook_id>{_common.GUID_REGEX})'
                                                 rf'/(?P<worksheet_id>{_common.GUID_REGEX})', re.IGNORECASE),
                                      dict()),
        Route.JOURNAL_WORKSTEP_LINK: (re.compile(rf'^/links', re.IGNORECASE), {'type': 'link_type',
                                                                               'workbook': 'workbook_id',
                                                                               'worksheet': 'worksheet_id',
                                                                               'workstep': 'workstep_id'}),
        Route.HOME: (re.compile(rf'^/(workbooks|(?P<folder_id>{_common.GUID_REGEX})/folder)', re.IGNORECASE),
                     dict()),
        Route.DATALAB_PROJECT: (
            re.compile(rf'/data-lab/(?P<datalab_project_id>{_common.GUID_REGEX})', re.IGNORECASE), dict())
    }

    @staticmethod
    def parse(url):
        address_match = SeeqURL.ADDRESS_REGEX.search(url)
        if not address_match:
            raise SPyRuntimeError(f'URL "{url}" does not start with typical http(s)://hostname(:port)')

        seeq_url = SeeqURL()
        groups = address_match.groupdict()
        seeq_url.protocol = HttpProtocol[groups['protocol'].upper()]
        seeq_url.hostname = groups['hostname']
        seeq_url.port = 80 if seeq_url.protocol == HttpProtocol.HTTP else 443
        if _common.present(groups, 'port'):
            seeq_url.port = int(groups['port'])

        path_and_parameters = url[address_match.end():].split('?')
        path = path_and_parameters[0]
        parameters = ''.join(path_and_parameters[1:]) if len(path_and_parameters) > 1 else None

        parameter_dict = dict()
        if parameters is not None:
            parameter_list = re.split(_common.HTML_AMPERSAND_REGEX, parameters)
            for parameter in parameter_list:
                parameter_parts = re.split(_common.HTML_EQUALS_REGEX, parameter)
                parameter_key = parameter_parts[0]
                parameter_value = parameter_parts[1] if len(parameter_parts) > 1 else None
                parameter_dict[parameter_key] = parameter_value

        seeq_url.route = Route.UNKNOWN
        for route in SeeqURL.ROUTES.keys():
            route_path_regex, route_parameters_dict = SeeqURL.ROUTES[route]
            route_match = route_path_regex.search(path)
            if not route_match:
                continue

            seeq_url.route = route
            groups = dict(route_match.groupdict())
            for parameter_key, parameter_value in parameter_dict.items():
                if parameter_key in route_parameters_dict:
                    groups[route_parameters_dict[parameter_key]] = parameter_value

            if route == Route.JOURNAL_WORKSTEP_LINK and groups['link_type'] != 'workstep':
                raise SPyValueError(f'Unknown JOURNAL_WORKSTEP_LINK type "{groups["link_type"]}"')

            seeq_url.folder_id = _common.get(groups, 'folder_id')
            seeq_url.workbook_id = _common.get(groups, 'workbook_id')
            seeq_url.worksheet_id = _common.get(groups, 'worksheet_id')
            seeq_url.workstep_id = _common.get(groups, 'workstep_id')
            seeq_url.datalab_project_id = _common.get(groups, 'datalab_project_id')

            break

        return seeq_url


def cleanse_url(url):
    parts = urlparse(url)  # type: ParseResult
    url = f'{parts.scheme}://{parts.hostname}'
    if parts.port is not None:
        if parts.port not in [80, 443] or \
                (parts.scheme.lower() == 'http' and parts.port != 80) or \
                (parts.scheme.lower() == 'https' and parts.port != 443):
            url += f':{parts.port}'

    return url


def parse_url(url):
    return SeeqURL.parse(url)


def get_workbook_id_from_url(url):
    """
    Get the Seeq ID of a workbook from a URL

    Given a URL copied from a browser or from an API response 'href' attribute,
    get the URL of the workbook.

    Parameters
    ----------
    url : str
        The URL

    Returns
    -------
    {str, None}
        The Seeq ID as a string, or None if no workbook ID was found
    """
    return SeeqURL.parse(url).workbook_id


def get_worksheet_id_from_url(url):
    """
    Get the Seeq ID of a worksheet from a URL

    Given a URL copied from a browser or from an API response 'href' attribute,
    get the URL of the worksheet.

    Parameters
    ----------
    url : str
        The URL

    Returns
    -------
    {str, None}
        The Seeq ID as a string, or None if no worksheet ID was found
    """
    return SeeqURL.parse(url).worksheet_id


def get_workstep_id_from_url(url):
    """
    Get the Seeq ID of a workstep from a URL

    Given a URL copied from a browser or from an API response 'href' attribute,
    get the URL of the workstep.

    Note that URLs from a browser rarely specify the workstep. URLs that
    contain the workstep normally come from links in Organizer Topic Documents
    or href attributes in API outputs.

    Parameters
    ----------
    url : str
        The URL

    Returns
    -------
    {str, None}
        The Seeq ID as a string, or None if no workstep ID was found
    """
    return SeeqURL.parse(url).workstep_id


def get_data_lab_project_id_from_url(url):
    """
    Get the Seeq DataLab Project ID from a URL

    Given a URL copied from a browser or from an API response 'href' attribute,
    get the URL of the DataLab project.

    Parameters
    ----------
    url : str
        The URL

    Returns
    -------
    {str, None}
        The Seeq ID as a string, or None if no project ID was found
    """
    return SeeqURL.parse(url).datalab_project_id
