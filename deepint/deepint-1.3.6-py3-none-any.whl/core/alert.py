#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import enum
from datetime import datetime
from typing import Any, List, Dict

from ..auth import Credentials
from ..error import DeepintBaseError
from ..util import handle_request, parse_date, parse_url


class AlertType(enum.Enum):
    """Available alert types in the system.
    """

    update = 0
    stall = 1

    @classmethod
    def from_string(cls, _str: str) -> 'AlertType':
        """Builds the :obj:`deepint.core.alert.AlertType` from a :obj:`str`.

        Args:
            _str: name of the alert type.

        Returns:
            the alert type converted to :obj:`deepint.core.alert.AlertType`.
        """

        return cls.unknown if _str not in [e.name for e in cls] else cls[_str]

    @classmethod
    def all(cls) -> List[str]:
        """ Returns all available alert types serialized to :obj:`str`.

        Returns:
            all available alert types
        """
        
        return [e.name for e in cls]


class AlertInfo:
    """Stores the information of a Deep Intelligence alert.
    
    Attributes:
        alert_id: alert's id in format uuid4.
        name: alert's name.
        description: alert's description.
        alert_type: type of alert (update, stall). Set to 'update' if you want to trigger when a source updated 
            on certain conditions. Set to 'stall' if you want to trigger when a source do not update for a long time.
        last_modified: Last modified date.
        created: Creation date.
        source_id: Identifier of associated source.
        color: Color for the alert
        condition: condition to trigger the alert.
        time_stall: Time in seconds when the alert should trigger (for stall). Must be at least 60.
        subscriptions: List of emails subscribed to the alert.
    """

    def __init__(self, alert_id: str, name: str, description: str, created: datetime, last_modified: datetime,
                 subscriptions: List[str], color: str, alert_type: AlertType, source_id: str, condition: Dict[str, Any],
                 time_stall: int) -> None:
        self.alert_id = alert_id
        self.name = name
        self.description = description
        self.created = created
        self.last_modified = last_modified
        self.subscriptions = subscriptions
        self.color = color
        self.alert_type = alert_type
        self.source_id = source_id
        self.condition = condition
        self.time_stall = time_stall

    def __eq__(self, other):
        if not isinstance(other, AlertInfo):
            return False
        else:
            return self.alert_id == other.alert_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'AlertInfo':
        """Builds a AlertInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized AlertInfo.

        Returns:
            AlertInfo containing the information stored in the given dictionary.
        """

        alert_id = obj.get("id")
        name = obj.get("name")
        description = obj.get("description")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        subscriptions = obj.get("subscriptions")
        color = obj.get("color")
        alert_type = AlertType.from_string(obj.get("type"))
        source_id = obj.get("source")
        condition = obj.get("condition")
        time_stall = int(obj.get("time_stall")) if obj.get("time_stall") is not None else None
        return AlertInfo(alert_id, name, description, created, last_modified, subscriptions, color, alert_type,
                         source_id, condition, time_stall)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.alert_id,
                "name": self.name,
                "description": self.description,
                "created": self.created.isoformat(),
                "last_modified": self.last_modified.isoformat(),
                "subscriptions": self.subscriptions,
                "color": self.color,
                "type": self.alert_type.name,
                "source": self.source_id,
                "condition": self.condition,
                "time_stall": int(self.time_stall)
                }


class AlertInstances:
    """Operates over the instances of a concrete alert.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.alert.Alert`
    
    Attributes:
        alert: the alert with which to operate with its instances
    """

    def __init__(self, alert: 'Alert'):
        self.alert = alert

    def fetch(self) -> List[Dict]:
        # request
        path = f'/api/v1/workspace/{self.alert.workspace_id}/alerts/{self.alert.info.alert_id}/instances'
        headers = {'x-deepint-organization': self.alert.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, parameters=parameters, credentials=self.alert.credentials)

        # format response
        return response


class Alert:
    """A Deep Intelligence alert.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.alert.Alert.build`
    or :obj:`deepint.core.alert.Alert.from_url` methods. 
    
    Attributes:
        organization_id: organization where alert is located.
        workspace_id: workspace where alert is located.
        info: :obj:`deepint.core.alert.AlertInfo` to operate with alert's information.
        instances: :obj:`deepint.core.alert.AlertInstances` to operate with alert's instances.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the alert. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, workspace_id: str, credentials: Credentials, info: AlertInfo) -> None:
        self.info = info
        self.credentials = credentials
        self.workspace_id = workspace_id
        self.organization_id = organization_id
        self.instances = AlertInstances(self)

    def __str__(self):
        return f'<Alert organization_id={self.organization_id} workspace={self.workspace_id} {self.info}>'

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return False
        else:
            return self.info == other.info

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, alert_id: str, credentials: Credentials = None) -> 'Alert':
        """Builds an alert.
        
        Note: when alert is created, the alert's information is retrieved from API.

        Args:
            organization_id: organization where alert is located.
            workspace_id: workspace where alert is located.
            alert_id: alert's id.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the alert. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the alert build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        alert_info = AlertInfo(alert_id=alert_id, name=None, description=None, created=None, last_modified=None,
                               subscriptions=None, color=None, alert_type=None, source_id=None, condition=None,
                               time_stall=None)
        alert = cls(organization_id=organization_id, workspace_id=workspace_id, credentials=credentials, info=alert_info)
        alert.load()
        return alert

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Alert':
        """Builds a alert from it's API or web associated URL.

        The url must contain the workspace's id and the alert's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d&s=alert&i=db98f976-f4bb-43d5-830e-bc18a3a89641
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42/alerts/db98f976-f4bb-43d5-830e-bc18a3a89641
        
        Note: when alert is created, the alert's information is retrieved from API.
            Also it is remmarkable that if the API URL is providen, the organization_id must be provided in the optional parameter, otherwise
            this ID won't be found on the URL and the Organization will not be created, raising a value error.

        Args:
            url: the alert's API or web associated URL.
            organization_id: the id of the organziation. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the alert. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the alert build with the URL and credentials.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info or 'alert_id' not in url_info:
            raise ValueError('Fields workspace_id and alert_id must be in url to build the object.')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)

        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], alert_id=url_info['alert_id'], credentials=new_credentials)

    def load(self):
        """Loads the alert's information.

        If the alert's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/alerts/{self.info.alert_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = AlertInfo.from_dict(response)

    def update(self, name: str = None, description: str = None, subscriptions: List[str] = None, color: str = None,
               alert_type: AlertType = None, source_id: str = None, condition: Dict[str, Any] = None, time_stall: int = None):
        """Updates a alert's attributes

        Args:
            name: alert's name. If not provided the alert's name stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            descrpition: alert's description. If not provided the alert's description stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            subscriptions: list of emails subscribed to the alert. If not provided the alert's subscriptions stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            color: alert's color. If not provided the alert's color stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            alert_type: alert's type. If not provided the alert's type stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            source_id: identifier of associated source. If not provided the alert's target source's id stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            condition: condition to trigger the alert. If not provided the alert's condition stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
            time_stall: time in seconds when the alert should trigger (for stall). If not provided the alert's time_stall stored in the :obj:`deepint.core.alert.Alert.alert_info` attribute is taken.
        """

        # check parameters
        name = name if name is not None else self.info.name
        color = color if color is not None else self.info.color
        description = description if description is not None else self.info.description
        subscriptions = subscriptions if subscriptions is not None else self.info.subscriptions
        source_id = source_id if source_id is not None else self.info.source_id
        alert_type = alert_type if alert_type is not None else self.info.alert_type
        condition = condition if condition is not None else self.info.condition
        time_stall = time_stall if time_stall is not None else self.info.time_stall

        if alert_type == AlertType.stall and time_stall is not None and time_stall < 60:
            raise DeepintBaseError(code='ALERT_CREATION_VALUES', message='Minimum alert time stall is 60 seconds.')

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/alerts/{self.info.alert_id}'
        headers = {'x-deepint-organization': self.organization_id}
        parameters = {
            'name': name,
            'description': description,
            'subscriptions': subscriptions,
            'color': color,
            'type': alert_type.name,
            'source': source_id,
            'condition': condition,
            'time_stall': time_stall
        }
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        # map results
        self.info.name = name
        self.info.description = description
        self.info.subscriptions = subscriptions
        self.info.alert_type = alert_type
        self.info.source_id = source_id
        self.info.condition = condition
        self.info.time_stall = time_stall

    def delete(self):
        """Deletes an alert.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace_id}/alerts/{self.info.alert_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info.to_dict()}
