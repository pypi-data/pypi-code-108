#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.


import datetime
from typing import Any, Dict

from .task import Task
from ..auth import Credentials
from ..util import handle_request, parse_url


class DashboardInfo:
    """Stores the information of a Deep Intelligence dashboard.
    
    Attributes:
        dashboard_id: dashboard's id in format uuid4.
        created: Creation date
        last_modified: last modified date
        last_access: last access date
        name: dashboard's name
        description: dashboard's description
        privacy: if 'private', dashboard only accesible for Organization's users
        share_opt: Option for the shared dashboard GUI
        ga_id: Opctional Google Analytics ID
        restricted: True to check for explicit permission for shared dashboard
        configuration: see documentation for advanced options.
    """

    def __init__(self, dashboard_id: str, created: datetime.datetime, last_modified: datetime.datetime, last_access: datetime.datetime,
                    name: str, description: str, privacy: str, share_opt: str, ga_id: str, restricted: bool,
                    configuration: Dict[str, Any] = {}) -> None:
        self.dashboard_id = dashboard_id
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.name = name
        self.description = description
        self.privacy = privacy
        self.share_opt = share_opt
        self.ga_id = ga_id
        self.restricted = restricted
        self.configuration = configuration
    
    def __eq__(self, other):
        if not isinstance(other, DashboardInfo):
            return False
        else:
            return self.dashboard_id == other.dashboard_id
    
    def __str__(self) -> str:
        return ' '.join([f'{k}={v}' for k,v in self.to_dict().items()])
    
    @staticmethod
    def from_dict(obj: Any) -> 'DashboardInfo':
        """Builds a 'DashboardInfo' with a dictionary.
        
        Args:
            obj: containing a serialized DashboardInfo.
        
        Returns: 
            DashboardInfo containing the information stored in the given dictionary.
        """

        dashboard_id = obj.get("id")
        created = obj.get("created")
        last_modified = obj.get("last_modified")
        last_access = obj.get("last_access")
        name = obj.get("name")
        description = obj.get("description")
        privacy = obj.get("privacy")
        share_opt = obj.get("share_opt")
        gaId = obj.get("gaId")
        restricted = obj.get("restricted")
        configuration = obj.get("configuration")

        return DashboardInfo(dashboard_id, created, last_modified, last_access, name, description,
                        privacy, share_opt, gaId, restricted, configuration)
    
    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing information stored in the current object.
        
        Returns:
            Dictionary containing the information stored in the current object.
        """

        return {"id": self.dashboard_id, "created": self.created, "last_modified": self.last_modified,
                "last_access": self.last_access, "name": self.name, "description": self.description, "privacy": self.privacy,
                "share_opt": self.share_opt, "gaId": self.ga_id, "restricted": self.restricted, "configuration": self.configuration }

class Dashboard:
    """"A Deep Intelligence Dashboard.
    
    Note: this class should not be instanced directly, and it´s recommended to use the 
    :obj:'deepint.core.dashboard.Dashboard.build()' of :obj:'deepint.core.dashboard.Dashboard.from_url()' methods
    
    Attributes: 
        organization_id: organization where the dashboard is located
        workspace_id: workspace where the dashboard is located
        info: :obj:'deepint.core.dashboard.DashboardInfo' to operate with dashboard's information
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform
                        over the source. If not provided, the credentials are generated with
                        :obj:'deepint.auth.credentials.Credentials.build'
    """

    def __init__(self, organization_id: str, workspace_id: str, info: DashboardInfo,
                credentials: Credentials) -> None:
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.info = info
        self.credentials = credentials

    def __str__(self) -> str:
        return f'<Dashboard organization={self.organization_id} workspace={self.workspace_id} {self.info}>'
    
    def __eq__(self, other):
        if not isinstance(other,Dashboard):
            return False
        else:
            return self.info == other.info
    
    @classmethod
    def build(cls, organization_id: str, workspace_id:str, dashboard_id: str, credentials: Credentials = None) -> 'Dashboard':
        """Builds a Dashboard.
        
        Note: when the dashboard is created, the dasboard's informatio is retrieved from API
        
        Args:
            organization_id: organization whre the dashboard is located
            workspace_id: workspace where the dashboard is located
            dashboard_id: dashboard's id
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations
            over the dashboard. If not provided, the credentials are generated with the :obj:'deepint.auth.credentials.Credentials.build'.
            
        Returns :
            The dashboard with the given parameters and credentials
        """

        credentials = credentials if credentials is not None else Credentials.build()
        d_info = DashboardInfo(dashboard_id=dashboard_id, created=None, last_access=None, last_modified=None,
                        name=None, description=None, privacy=None, share_opt=None, ga_id=None, restricted=False, configuration={})
        dash = cls(organization_id=organization_id, workspace_id=workspace_id, info=d_info, credentials=credentials)
        dash.load()

        return dash
    
    def load(self):
        """Load the dashboard's information.
        
        If the dashboard information is already loaded, it's replaced by the new after retrieval
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/dashboard/{self.info.dashboard_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = DashboardInfo.from_dict(response)
    
    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Dashboard':
        """Builds a dashboard from its api or web asspciated URL.
        
        The url must contain the workspace's id and the dashboard's id as in the following example
        
        Example:
             - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d&s=dashboard&i=db98f976-f4bb-43d5-830e-bc18a3a89641
             - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/dashboard/db98f976-f4bb-43d5-830e-bc18a3a89641
            
        Note: when the dashboard is created, the dashboard's information is retrieved from API
        
        Args: 
            url: the dashboard's api or web associated URL
            organization_id: the id of the organziation. Must be providen if the API URL is used
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations
            over the source. If not provided, the credentials are generated with :obj:'deepint.auth.credentials.Credentials.build'
            
        Returns:
            The dashboard with the URL and credentials
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Field organization_id must be in url to build the object. Or providen as an optional parameter')
        if 'workspace_id' not in url_info or 'dashboard_id' not in url_info:
            raise ValueError('Fields workspace_id and dashboard_id must be in url to build the object')
        
        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)

        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], dashboard_id=url_info['dashboard_id'],
                            credentials=new_credentials)
    
    def update(self, name: str = None, description: str = None, privacy: str = 'public', share_opt: str = "", ga_id: str = None, restricted: bool = None, configuration: Dict[str, Any] = {}):
        """Updates a dashboard's information.
        
        Args:
            name: dashboard's name. If not provided the dashboard's name the dashboard's name stored in the :obj:'deepint.core.dashboard.Dashboard.dashboard_info' attribute is taken
            description: dashboard's description. If not provided the dashboard's name the dashboard's description stored in the :obj:'deepint.core.dashboard.Dashboard.dashboard_info' attribute is taken
            privacy: Determine if the dashboard is public or private
            share_opt: Option for the shared dashboard GUI
            gaID: optional Google Analytics ID
            restricted: True to check for explicit permission for shared dashboard
            configuration:
        """

        # check parameters
        name = name if name is not None else self.info.name
        description = description if description is not None else self.info.description
        privacy = privacy if privacy is not None else self.info.privacy
        share_opt = share_opt if share_opt is not None else self.info.share_opt
        ga_id = ga_id if ga_id is not None else self.info.ga_id
        restricted = restricted if restricted is not None else self.info.restricted
        configuration = configuration if configuration is not None else self.info.configuration

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/dashboard/{self.info.dashboard_id}'
        parameters = {'name': name, 'description': description, 'privacy': privacy, 'share_opt': share_opt,
                        'gaId': ga_id, 'restricted': restricted, 'configuration': configuration}
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        # update local state
        self.info.name = name
        self.info.description = description
        self.info.privacy = privacy
        self.info.share_opt = share_opt
        self.info.ga_id = ga_id
        self.info.restricted = restricted
        self.info.configuration = configuration

    def clone(self, name:str = None) -> 'Dashboard':
        """Clones a dashboard.
        
        Args:
            name: name for the new dashboard. If not providen the name will be `Copy of <current dashboard's name>`

        Returns:
            the cloned dashboard instance.
        """

        # generate name fi not present
        if name is None:
            name = f'Copy of {self.info.name}'

        # request dashboard clone
        path = f'/api/v1/workspace/{self.workspace_id}/dashboard/{self.info.dashboard_id}/clone'
        parameters = {'name': name}
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='POST', path=path, headers=headers,credentials=self.credentials)

        new_dashboard = Dashboard.build(organization_id=self.organization_id, workspace_id=self.workspace_id,
                                         dashboard_id=response['dashboard_id'],credentials=self.credentials)
        return new_dashboard
            
    def delete(self):
        """Deletes a dashboard.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/dashboard/{self.info.dashboard_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)
    
    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in the current object.
        
        Returns: 
            dictionary containing the information stored in the current object.
        """

        return {"info": self.info.to_dict()}

    def fetch_all(self, force_reload: bool = False) -> 'DashboardInfo':
        """Retrieves all dashboard's information.
        
        Args: 
            force_reload: if set to True, info is reloaded before the search with the :obj:'depint.core.dashboard.DashboardInfo.load' method
            
        Returns:
            the dashboard's info
        """

        # if set to true reload
        if force_reload:
            self.load()

        return self.info