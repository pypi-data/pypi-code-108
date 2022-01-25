#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.


import warnings
import numpy as np
from datetime import datetime, date
from typing import Any, List, Dict, Type, Optional
from dateutil.parser import parse as python_date_parser

from .task import Task
from ..auth import Credentials
from ..error import DeepintBaseError
from ..util import handle_request, parse_date, parse_url


warnings.simplefilter(action='ignore', category=FutureWarning)


class VisualizationInfo:
    """Stores the information of a Deep Intelligence  visualization
    
    Attributes: 
        visualization_id: visualization's id in format uuid4.
        created: Creation date
        last_modified: last modified date
        last_access: last access date
        name: visualization's name
        description: visualization's description
        visualization_type: visualization's type
        public: if false, visualization only accesible for Organization's users
        source_id: source's id with the info for the visualization
        configuration: 
    """
    
    def __init__(self, visualization_id: str, created: datetime, last_modified: datetime,
                last_access: datetime, name: str, description: str,
                visualization_type: str, public: bool, source_id: str, configuration: str) -> None:

        self.visualization_id = visualization_id
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.name = name
        self.description = description
        self.visualization_type = visualization_type
        self.public = public
        self.source_id = source_id
        self.configuration = configuration

    def __eq__(self, other):
        if not isinstance(other, VisualizationInfo):
            return False
        else:
            return self.visualization_id == other.visualization_id

    def __str__(self) -> str:
        return ' '.join([f'{k}={v}' for k,v in self.to_dict().items()])
        
    @staticmethod
    def from_dict(obj: Any) -> 'VisualizationInfo':
        """Builds a 'VisualizationInfo' with a dictionary.
        
        Args: 
            obj: :obj:'object' or :obj:'dict' containing the a serialized VisualizationInfo.
            
        Returns: 
            VisualizationInfo containing the information stored in the given dictionary.
        """

        visualization_id = obj.get("id")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        last_access = parse_date(obj.get("last_access"))
        name = obj.get("name")
        description = obj.get("description")
        visualization_type = obj.get("type")
        public = obj.get("public")
        source_id = obj.get("source")
        configuration = obj.get("configuration")
        return VisualizationInfo(visualization_id, created, last_modified, last_access, name, 
            description, visualization_type, public, source_id, configuration)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing de information stored in the current object.
        
        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.visualization_id, "created": self.created,"last_modified": self.last_modified, "last_access": self.last_access,
                "name": self.name, "description": self.description, "type": self.visualization_type,
                "public": self.public, "source": self.source_id, "configuration": self.configuration }


class Visualization:
    """ A Deep Intelligence Visualization
    
    Note: this class should not be instanced directly, and it's recommended to use the 
    :obj:'deepint.core.visualization.Visualization.build()' or :obj:'deepint.core.visualization.Visualization.from_url' methods
    
    Attributes:
        organization_id: organization where visualization is located
        workspace_id: workspace where visualization is located
        info: :obj:'deepint.core.visualization.VisualizationInfo' to operate with visualization's information.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operation over the source.
                        if not provided, the credentials are generated with the :obj:'deepint.auth.credentials.Credentials.build'.
                        
    """

    def __init__(self, workspace_id: str, organization_id: str,
                    info: VisualizationInfo, credentials: Credentials) -> None:
        self.info = info
        self.organization_id = organization_id
        self.credentials = credentials
        self.workspace_id = workspace_id
        
    def __str__(self) -> str:
        return f'<Visualization organization={self.organization_id} workspace={self.workspace_id} {self.info}>'

    def __eq__(self, other):
        if not isinstance(other, Visualization):
            return False
        else: 
            return self.info == other.info

    @classmethod
    def build(cls, workspace_id: str, organization_id: str, visualization_id: str, credentials: Credentials = None) -> 'Visualization':
        """Builds a visualization.
        
        Note: when visualization is created, the visualization's information is retrieved from API
        
        Args:
            organization_id: organization where visualization is located
            workspace_id: workspace where the visualization is located
            visualization_id: visualziation's id
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations
            over the visualization. If not provided, the credentials are generated with the :obj:'deepint.auth.credentials.Credentials.build'.
            
            
        Returns: 
            the visualization with the given parameters and credentials.
        """
        credentials = credentials if credentials is not None else Credentials.build()
        v_info = VisualizationInfo(visualization_id=visualization_id, created=None, last_modified= None, last_access= None,
                                    name=None, description=None, visualization_type=None, public=None,
                                    source_id=None, configuration=None)
        visu = cls(organization_id=organization_id, workspace_id= workspace_id, credentials=credentials, info=v_info)
        visu.load()
        return visu

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Visualization':
        """Builds a visualization from its  API or web associated URL.
        
        The url must contain the workspace's id and the visualization's id as in the following example.
        
        Example
            - https://app.deepint.net/o/57a4c194-3d4d-4125-904b-8a2b2a56a7c2?ws=edcc4ef4-b85a-4899-89e8-8431af98ad56&s=visualization&i=bfff6a5f-0bd2-46cd-84b7-6cf7692957a8
            - https://app.deepint.net/api/v1/workspace/15b74790-4b2c-4ccb-9205-30d1af8d0c35/visualization/e14720cb-c645-4d05-b403-4212a5e625c5
        
        Note: when the visualization is created, the visualization's information is retrieved from API
        
        Args:
            url: the visualization's API or web associated URL
            organization_id: the id of the organization. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations
            over the source. If not provided, the credentials are generated with :obj:'deepint.auth.credentials.Credentials.build'
            
        Returns:
            The visualization with the url and credentials
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Field organization_id must be in url to build the object. Or providen as an optional parameter')

        if 'workspace_id' not in url_info or 'visualization_id' not in url_info:
            raise ValueError('Fields workspace_id, visualization_id and organization_id must be in url to build the object')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)

        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], visualization_id=url_info['visualization_id'],
                            credentials=new_credentials)

    def load(self) -> None:
        """Load th visualization's information.
        
        If the visualization's information is already loaded, it's replaced by the new one after retrieval.
        """

        #request
        path = f'/api/v1/workspace/{self.workspace_id}/visualization/{self.info.visualization_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, credentials=self.credentials, headers=headers)

        #map results
        self.info = VisualizationInfo.from_dict(response)

    def update(self, name: str = None, description: str = None, privacy: str = 'public', source: str = None, configuration: Dict[str,Any] = {} ):
        """Updates a visualization's name and description.
        
        Args:
            name: visualization's name. If not provided the visualziation's name stored in the :obj:'deepint.core.visualization.Visualization.visualization_info'
                attribute is taken. 
            description: visualization's description. If not provided de visualization's description stored in the :obj:'deepint.core.visualization.Visualization.visualization_info'
                attribute is taken.
            privacy: Determine if the visualization is public or private
            source: id from the source to use in the visualization
            configuration: Dictionary
        """

        #Check parameters
        name = name if name is not None else self.info.name
        privacy = privacy if privacy is not None else self.info.public
        source = source if source is not None else self.info.source_id
        description = description if description is not None else self.info.description
        configuration = configuration if configuration is not None else self.info.configuration
        
        #request
        path = f'/api/v1/workspace/{self.workspace_id}/visualization/{self.info.visualization_id}'
        parameters = {'name': name, 'description': description, 'privacy': privacy, 'source': source, 'configuration': configuration}
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)
        
        #update local state
        self.info.name = name
        self.info.description = description
        self.info.public = privacy
        self.info.source_id = source
        self.info.configuration = configuration

    def clone(self, name:str = None) -> 'Visualization':
        """Clones a visualization.
        
        Args:
            name: name for the new visualization. If not providen the name will be `Copy of <current visualization's name>`
        
        Returns:
            the cloned visualization instance.
        """

        # generate name fi not present
        if name is None:
            name = f'Copy of {self.info.name}'

        # request visualization clone
        path = f'/api/v1/workspace/{self.workspace_id}/visualization/{self.info.visualization_id}/clone'
        parameters = {'name': name}
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='POST', path=path, headers=headers,credentials=self.credentials)

        new_visualization = Visualization.build(organization_id=self.organization_id, workspace_id=self.workspace_id,
                                         visualization_id=response['visualization_id'],credentials=self.credentials)
        return new_visualization
        
    def delete(self) -> None:
        """Deletes a visualization.
        """

        #request
        path = f'/api/v1/workspace/{self.workspace_id}/visualization/{self.info.visualization_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in the current object.
        
        Returns:
            dictionaty containing the information stored in the current object.
        """

        return {"info": self.info.to_dict()}