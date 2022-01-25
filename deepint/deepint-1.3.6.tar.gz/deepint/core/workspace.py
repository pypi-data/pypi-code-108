#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import os
import requests
import pandas as pd
from datetime import datetime
from typing import Any, List, Dict, Optional, Generator, Union

from .dashboard import Dashboard
from .task import Task, TaskStatus
from .alert import Alert, AlertType
from .visualization import Visualization
from .model import Model, ModelMethod, ModelType
from .source import Source, SourceFeature, FeatureType

from ..auth import Credentials
from ..error import DeepintBaseError
from ..util import handle_request, handle_paginated_request, parse_date, parse_url


class WorkspaceInfo:
    """Stores the information of a Deep Intelligence workspace.
    
    Attributes:
        workspace_id: workspace's id in format uuid4.
        created: Creation date.
        last_modified: Last modified date.
        last_access: Last access date.
        name: source's name.
        description: source's description.
        size_bytes: workspace size in bytes.
        sources_count: number of sources in the workspace.
        dashboards_count: number of dashboard in the workspace.
        visualizations_count: number of visualizations in the workspace.
        models_count:  number of models in the workspace.
    """

    def __init__(self, workspace_id: str, name: str, description: str, created: datetime, last_modified: datetime,
                 last_access: datetime, sources_count: int, dashboards_count: int, visualizations_count: int,
                 models_count: int, size_bytes: int) -> None:
        self.workspace_id = workspace_id
        self.name = name
        self.description = description
        self.created = created
        self.last_modified = last_modified
        self.last_access = last_access
        self.sources_count = sources_count
        self.dashboards_count = dashboards_count
        self.visualizations_count = visualizations_count
        self.models_count = models_count
        self.size_bytes = size_bytes

    def __eq__(self, other):
        if not isinstance(other, WorkspaceInfo):
            return False
        else:
            return self.workspace_id == other.workspace_id

    def __str__(self):
        return ' '.join([f'{k}={v}' for k, v in self.to_dict().items()])

    @staticmethod
    def from_dict(obj: Any) -> 'WorkspaceInfo':
        """Builds a WorkspaceInfo with a dictionary.

        Args:
            obj: :obj:`object` or :obj:`dict` containing the a serialized WorkspaceInfo.

        Returns:
            WorkspaceInfo containing the information stored in the given dictionary.
        """

        workspace_id = obj.get("id")
        name = obj.get("name")
        description = obj.get("description")
        created = parse_date(obj.get("created"))
        last_modified = parse_date(obj.get("last_modified"))
        last_access = parse_date(obj.get("last_access"))
        sources_count = int(obj.get("sources_count"))
        dashboards_count = int(obj.get("dashboards_count"))
        visualizations_count = int(obj.get("visualizations_count"))
        models_count = int(obj.get("models_count"))
        size_bytes = int(obj.get("size_bytes"))
        return WorkspaceInfo(workspace_id, name, description, created, last_modified, last_access, sources_count,
                             dashboards_count, visualizations_count, models_count, size_bytes)

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary containing the information stored in the current object.
        """

        return {"id": self.workspace_id, "name": self.name, "description": self.description,
                "created": self.created.isoformat(), "last_modified": self.last_modified.isoformat(),
                "last_access": self.last_access.isoformat(), "sources_count": int(self.sources_count),
                "dashboards_count": int(self.dashboards_count),
                "visualizations_count": int(self.visualizations_count), "models_count": int(self.models_count),
                "size_bytes": int(self.size_bytes)}


class WorkspaceVisualizations:
    """Operates over the visualizations of a concrete workspace.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.workspace.Workspace`.
    
    Attributes:
        workspace: the workspace with which to operate with its visualizations.
    """

    def __init__(self, workspace: 'Workspace', visualizations: List[Visualization]):
        self.workspace = workspace
        self._generator = None
        self._visualizations = visualizations

    def create(self, name: str, description: str, privacy: str, source: str, configuration: Dict[str, Any] = {}) -> Visualization:
        """Creates a visualization in current workspace.
        
        Args:
            name: new visualization's name.
            description: new visualization's description.
            
        Returns:
            The created visualization
        """
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/visualizations'
        parameters = {'name': name, 'description': description, 'privacy': privacy, 'source': source, 'configuration': configuration}
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.workspace.credentials)

        #map results
        new_visualization = Visualization.build(workspace_id=self.workspace.info.workspace_id, visualization_id=response['visualization_id'],
                            organization_id=self.workspace.organization_id, credentials=self.workspace.credentials)
        
        #update local state
        self._visualizations = self._visualizations if self._visualizations is not None else []
        self._visualizations.append(new_visualization)
        
        return new_visualization
    
    def load(self) -> None:
        """Loads a workspace's visualizations.

        If the visualizations were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/visualizations'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_paginated_request(method='GET', path=path, headers=headers, credentials=self.workspace.credentials)

        # map results
        self._visualizations = None
        self._generator = (Visualization.build(workspace_id=self.workspace.info.workspace_id, visualization_id=v['id'],
                                                organization_id=self.workspace.organization_id, source_id=None, credentials=self.workspace.credentials) for v in response)

    def fetch(self, visualization_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Visualization]:
        """Search for a visualization in the workspace.

        The first time is invoked, builds a generator to retrieve visualizations directly from deepint.net API. However, 
        if there is stored visualizations and the force_reload option is not specified, only iterates in local 
        visualizations. In other case, it request the visualizations to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            visualization_id: visualization's id to search by.
            name: visualization's name to search by.
            force_reload: if set to True, visualizations are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceVisualizations.load` method.
        
        Returns:
            retrieved visualization if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if visualization_id is None and name is None:
            return None

        # search by given attributes
        if self._visualizations is not None and not force_reload:
            for v in self._visualizations:
                if v.info.visualization_id == visualization_id or v.info.name == name:
                    return v

        if self._generator is not None:
            for v in self._generator:
                if v.info.visualization_id == visualization_id or v.info.name == name:
                    return v

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Visualization, None, None]:
        """Retrieves all workspace's visualizations.
        
        The first time is invoked, builds a generator to retrieve visualizations directly from deepint.net API. However, 
        if there is stored visualizations and the force_reload option is not specified, only iterates in local 
        visualizations. In other case, it request the visualizations to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, visualizations are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceVisualization.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Visualization`: The next visualization returned by deeepint.net API.

        Returns:
            the workspace's visualizations.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._visualizations is None:
            yield from self._generator
        else:
            yield from  self._visualizations


class WorkspaceDashboards:
    """Operates over the dashboards of a concrete workspace.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.workspace.Workspace`.
    
    Attributes:
        workspace: the workspace with which to operate with its dashboards.
    """

    def __init__(self, workspace: 'Workspace', dashboards: List[Dashboard]):
        self.workspace = workspace
        self._generator = None
        self._dashboards = dashboards
    
    def create(self, name: str, description: str, privacy: str, share_opt: str, restricted: bool, ga_id: str = None, configuration: Dict[str, Any] = {}) -> Dashboard:
        """Creates a dashboard in the current workspace.
        
        Args
            name: new dashboard's name
            description: new dashboard's description
            privacy: new dashboard's privacy
            share_opt: Option for the shared dashboard GUI
            ga_id: Opctional Google Analytics ID
            restricted: True to check for explicit permission for shared dashboard
            configuration: advanced option.
        
        Returns: 
            The created dashboard
        """

        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/dashboards'
        parameters = {'name': name, 'description': description, 'privacy': privacy, 'shareOpt': share_opt, 'gaId': ga_id, 'restricted': restricted, 'configuration': configuration}
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_request(method='POST', path=path, parameters=parameters, headers=headers, credentials=self.workspace.credentials)
        
        # map result
        new_dashboard = Dashboard.build(workspace_id=self.workspace.info.workspace_id, organization_id=self.workspace.organization_id,
                                        dashboard_id=response['dashboard_id'], credentials=self.workspace.credentials)
        
        # update local state
        self._dashboards = self._dashboards if self._dashboards is not None else []
        self._dashboards.append(new_dashboard)

        return new_dashboard

    def load(self):
        """Loads a workspace's dashboards.

        If the dashboards were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/dashboards'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_paginated_request(method='GET', path=path, headers=headers, credentials=self.workspace.credentials)

        # map results
        self.dashboards = None
        self._generator = (Dashboard.build(organization_id=self.workspace.organization_id, workspace_id=self.workspace.info.workspace_id,
                         dashboard_id=d['id'], credentials=self.workspace.credentials) for d in response)
        
    def fetch(self, dashboard_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Dashboard]:
        """Search for a dashboard in the workspace.

        The first time is invoked, builds a generator to retrieve dashboards directly from deepint.net API. However, 
        if there is stored dashboards and the force_reload option is not specified, only iterates in local 
        dashboards. In other case, it request the dashboards to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            dashboard_id: dashboard's id to search by.
            name: dashboard's name to search by.
            force_reload: if set to True, dashboards are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceDashboards.load` method.
        
        Returns:
            Retrieved dashboard if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if dashboard_id is None and name is None:
            return None

        # search by given attributes
        if self._dashboards is not None and not force_reload:
            for d in self._dashboards:
                if d.info.dashboard_id == dashboard_id or d.info.name == name:
                    return d

        if self._generator is not None:
            for d in self._generator:
                if d.info.dashboard_id == dashboard_id or d.info.name == name:
                    return d

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Dashboard, None, None]:
        """Retrieves all workspace's dashboards.
        
        The first time is invoked, builds a generator to retrieve dashboards directly from deepint.net API. However, 
        if there is stored dashboards and the force_reload option is not specified, only iterates in local 
        dashboards. In other case, it request the dashboards to deepint.net API and iterates over it.
        
        Args:
            force_reload: if set to True, dashboards are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceDashboard.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Dashboard`: The next dashboard returned by deeepint.net API.

        Returns:
            the workspace's dashboards.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._dashboards is None:
            yield from self._generator
        else:
            yield from  self._dashboards


class WorkspaceSources:
    """Operates over the sources of a concrete workspace.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.workspace.Workspace`.
    
    Attributes:
        workspace: the workspace with which to operate with its sources.
    """

    def __init__(self, workspace: 'Workspace', sources: List[Source]):
        self.workspace = workspace
        self._generator = None
        self._sources = sources

    def load(self):
        """Loads a workspace's sources.

        If the sources were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/sources'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_paginated_request(method='GET', path=path, headers=headers, credentials=self.workspace.credentials)

        # map results
        self._sources = None
        self._generator = (Source.build(workspace_id=self.workspace.info.workspace_id, source_id=s['id'],
                                        organization_id=self.workspace.organization_id, 
                                        credentials=self.workspace.credentials) for s in response)

    def create(self, name: str, description: str, features: List[SourceFeature]) -> Source:
        """Creates a source in current workspace.

        Before creation, the source is loaded and stored locally in the internal list of sources in the current instance.

        Args:
            name: new source's name.
            descrpition: new source's description.
            features: list of source's features.
        
        Returns:
            the created source
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/sources'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        parameters = {'name': name, 'description': description, 'features': [f.to_dict_minimized() for f in features]}
        response = handle_request(method='POST', path=path, headers=headers, credentials=self.workspace.credentials, parameters=parameters)

        # map results
        new_source = Source.build(source_id=response['source_id'], workspace_id=self.workspace.info.workspace_id,
                                  organization_id=self.workspace.organization_id, credentials=self.workspace.credentials)

        # update local state
        self._sources = self._sources if self._sources is not None else []
        self._sources.append(new_source)

        return new_source

    def create_and_initialize(self, name: str, description: str, data: pd.DataFrame,
                              date_formats: Dict[str, str] = None, wait_for_initialization: bool = True) -> Source:
        """Creates a source in current workspace, then initializes it.

        Before creation, the source is loaded and stored locally in the internal list of sources in the current instance.

        Args:
            name: new source's name.
            descrpition: new source's description.
            data: data to in initialize the source. The source's feature names and data types are extracted from the given DataFrame.
            date_formats: dicionary contianing the association between feature (column name) and date format like the ones specified 
                in [#/date_formats]. Is optional to provide value for any column, but if not provided will be considered as 
                null and the date format (in case of being a date type) will be the default one assigned by Deep Intelligence.
            wait_for_initialization: if set to True, before the source creation, it waits for the source to update it's instances. In 
                other case, only the source is created, and then is returned without any guarantee that the instances have been 
                inserted into the source.

        Returns:
            the created and initialized (if wait_for_initialization is set to True) source.
        """

        # create features from dataframe
        features = SourceFeature.from_dataframe(data, date_formats=date_formats)

        # create source
        source = self.create(name=name, description=description, features=features)

        # update data in source
        task = source.instances.update(data=data)
        if wait_for_initialization:
            task.resolve()

        return source

    def create_if_not_exists(self, name: str) -> Source:
        """Creates a source and initializes it, if it doesn't exist any source with same name. 
        
        The source is created with the :obj:`deepint.core.worksapce.WorkspaceSources.create`, so it's reccomended to 
        read the documentation of that method to learn more about the possible artguments of creation.
        Before creation, the source is loaded and stored locally in the internal list of sources in the current instance.

        Args:
            name: new source's name.

        Returns:
            the created source.
        """

        # retrieve selected source
        selected_source = self.fetch(name=name, force_reload=True)

        # if exists return
        if selected_source is not None:
            return selected_source

        # if not exists, create
        return self.create(name, '', [])

    def create_else_update(self, name:str, data: pd.DataFrame, delete_instances_on_feature_update: bool = True, **kwargs) -> Source:
        """Creates a source and initializes it, if it doesn't exist any source with same name. Else updates the source's instances. 
        
        The source is created with the :obj:`deepint.core.worksapce.WorkspaceSources.create_and_initialize`, so it's 
        reccomended to read the documentation of that method to learn more about the possible arguments of creation  (that can be 
        providen in kwargs). Before creation, the source is loaded and stored locally in the internal list of sources in the 
        current instance. Also it's remmarkable that the source instance's are updated with the :obj:`deepint.core.source.SourceInstances.update`
        method, so it's reccomended to read the documentation of that method to learn more about the possible arguments of update (that 
        can be providen in the kwargs).

        Note: if features change, then the source instances are deleted

        Args:
            name: source's name.
            data: data to in initialize the source. The source's feature names and data types are extracted from the given DataFrame. It the source also created, is updated with the given data.
            delete_instances_on_feature_update: if set to False the instances are not deleted on features change.

        Returns:
            the affected source, updated if it was existing and created and initialized (if wait_for_initialization is providen and set to True) in other case.
        """

        # retrieve selected source
        selected_source = self.fetch(name=name, force_reload=True)

        # if exists update else create
        if selected_source is not None:
            
            # calculate features
            new_features = SourceFeature.from_dataframe(df=data)

            # update features if changed
            for f in new_features:
                current_feature = selected_source.features.fetch(name=f.name)
                if (current_feature is None) or (f != current_feature):

                    # delete previous instances
                    if delete_instances_on_feature_update:
                        selected_source.instances.clean()

                    # update features
                    t = selected_source.features.update(features=new_features)
                    t.resolve()

                    # update source
                    selected_source.load()
                    selected_source.features.load()

                    break

            # update source instances
            selected_source.instances.update(data=data,**kwargs)

        else:
            selected_source = self.create_and_initialize(name, '', data, **kwargs)

        return selected_source


    def fetch(self, source_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Source]:
        """Search for a source in the workspace.

        The first time is invoked, builds a generator to retrieve sources directly from deepint.net API. However, 
        if there is stored sources and the force_reload option is not specified, only iterates in local 
        sources. In other case, it request the sources to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            source_id: source's id to search by.
            name: source's name to search by.
            force_reload: if set to True, sources are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceSources.load` method.
        
        Returns:
            retrieved source if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if source_id is None and name is None:
            return None

        # search by given attributes
        if self._sources and self._sources is not None and not force_reload:
            for s in self._visualizations:
                if s.info.source_id == source_id or s.info.name == name:
                    return s

        if self._generator is not None:
            for s in self._generator:
                if s.info.source_id == source_id or s.info.name == name:
                    return s

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Source, None, None]:
        """Retrieves all workspace's sources.
        
        The first time is invoked, builds a generator to retrieve sources directly from deepint.net API. However, 
        if there is stored sources and the force_reload option is not specified, only iterates in local 
        sources. In other case, it request the sources to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, sources are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceSource.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Source`: The next source returned by deeepint.net API.

        Returns:
            the workspace's sources.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._sources is None:
            yield from self._generator
        else:
            yield from  self._sources


class WorkspaceTasks:
    """Operates over the tasks of a concrete workspace.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.workspace.Workspace`.
    
    Attributes:
        workspace: the workspace with which to operate with its tasks.
    """

    def __init__(self, workspace: 'Workspace', tasks: List[Task]):
        self.workspace = workspace
        self._generator = None
        self._tasks = tasks

    def load(self):
        """Loads a workspace's tasks.

        If the tasks were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/tasks'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_paginated_request(method='GET', path=path, headers=headers, credentials=self.workspace.credentials)

        # map results
        self._tasks = None
        self._generator = (
            Task.build(organization_id=self.workspace.organization_id, workspace_id=self.workspace.info.workspace_id, 
                       credentials=self.workspace.credentials, task_id=t['id']) for t in response)

    def fetch(self, task_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Task]:
        """Search for a task in the workspace.

        The first time is invoked, builds a generator to retrieve tasks directly from deepint.net API. However, 
        if there is stored tasks and the force_reload option is not specified, only iterates in local 
        tasks. In other case, it request the tasks to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            task_id: task's id to search by.
            name: task's name to search by.
            force_reload: if set to True, tasks are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceTasks.load` method.
        
        Returns:
            retrieved task if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if task_id is None and name is None:
            return None

        # search by given attributes
        if self._tasks is not None and not force_reload:
            for t in self._tasks:
                if t.info.task_id == task_id or t.info.name == name:
                    return t

        if self._generator is not None:
            for t in self._generator:
                if t.info.task_id == task_id or t.info.name == name:
                    return t

        return None

    def fetch_by_status(self, status: TaskStatus, force_reload: bool = False) -> Generator[Task, None, None]:
        """Search for a task in the workspace by status.

        The first time is invoked, builds a generator to retrieve tasks directly from deepint.net API. However, 
        if there is stored tasks and the force_reload option is not specified, only iterates in local 
        tasks. In other case, it request the tasks to deepint.net API and iterates over it.

        Args:
            status: task's status to search by.
            force_reload: if set to True, tasks are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceTasks.load` method.
        
        Returns:
            list of tasks in the given status if found, and in other case an empty list.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        for t in self._tasks:
            if t.info.status == status:
                yield t

    def fetch_all(self, force_reload: bool = False) -> Generator[Task, None, None]:
        """Retrieves all workspace's tasks.
        
        The first time is invoked, builds a generator to retrieve tasks directly from deepint.net API. However, 
        if there is stored tasks and the force_reload option is not specified, only iterates in local 
        tasks. In other case, it request the tasks to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, tasks are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceTask.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Task`: The next task returned by deeepint.net API.

        Returns:
            the workspace's tasks.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._tasks is None:
            yield from self._generator
        else:
            yield from  self._tasks

class WorkspaceAlerts:
    """Operates over the alerts of a concrete workspace.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.workspace.Workspace`.
    
    Attributes:
        workspace: the workspace with which to operate with its alerts.
    """

    def __init__(self, workspace: 'Workspace', alerts: List[Alert]):
        self.workspace = workspace
        self._generator = None
        self._alerts = alerts

    def load(self):
        """Loads a workspace's alerts.

        If the alerts were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/alerts'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_paginated_request(method='GET', path=path, headers=headers, credentials=self.workspace.credentials)

        # map results
        self._alerts = None
        self._generator = (
            Alert.build(organization_id=self.workspace.organization_id, workspace_id=self.workspace.info.workspace_id, 
                        credentials=self.workspace.credentials, alert_id=a['id']) for a in response)

    def create(self, name: str, description: str, subscriptions: List[str], color: str, alert_type: AlertType,
               source_id: str, condition: dict = None, time_stall: int = None) -> Alert:
        """Creates an alert in current workspace.

        Before creation, the alert is loaded and stored locally in the internal list of alerts in the current instance.

        Args:
            name: alert's name.
            description: alert's description.
            subscriptions: List of emails subscribed to the alert.
            color: Color for the alert
            alert_type: type of alert (update, stall). Set to 'update' if you want to trigger when a source updated 
                on certain conditions. Set to 'stall' if you want to trigger when a source do not update for a long time.
            source_id: Identifier of associated source.
            condition: condition to trigger the alert.
            time_stall: Time in seconds when the alert should trigger (for stall). Must be at least 60.

        Returns:
            the created alert
        """

        # check parameters
        if time_stall is not None and time_stall < 60:
            raise DeepintBaseError(code='ALERT_CREATION_VALUES', message='Minimum alert time stall is 60 seconds.')

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/alerts'
        headers = {'x-deepint-organization': self.workspace.organization_id}
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
        response = handle_request(method='POST', path=path, headers=headers, credentials=self.workspace.credentials, parameters=parameters)

        # map results
        new_alert = Alert.build(organization_id=self.workspace.organization_id, workspace_id=self.workspace.info.workspace_id, 
                                credentials=self.workspace.credentials, alert_id=response['alert_id'])

        # update local state
        self._alerts = self._alerts if self._alerts is not None else []
        self._alerts.append(new_alert)

        return new_alert

    def fetch(self, alert_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Alert]:
        """Search for a alert in the workspace.

        The first time is invoked, buidls a generator to retrieve alerts directly from deepint.net API. However, 
        if there is stored alerts and the force_reload option is not specified, only iterates in local 
        alerts. In other case, it request the alerts to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            alert_id: alert's id to search by.
            name: alert's name to search by.
            force_reload: if set to True, alerts are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceAlerts.load` method.
        
        Returns:
            retrieved alert if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if alert_id is None and name is None:
            return None

        # search by given attributes
        if self._alerts is not None and not force_reload:
            for a in self._alerts:
                if a.info.alert_id == alert_id or a.info.name == name:
                    return a

        if self._generator is not None:
            for a in self._generator:
                if a.info.alert_id == alert_id or a.info.name == name:
                    return a

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Alert, None, None]:
        """Retrieves all workspace's alerts.
        
        The first time is invoked, buidls a generator to retrieve alerts directly from deepint.net API. However, 
        if there is stored alerts and the force_reload option is not specified, only iterates in local 
        alerts. In other case, it request the alerts to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, alerts are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceAlert.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Alert`: The next alert returned by deeepint.net API.

        Returns:
            the workspace's alerts.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._alerts is None:
            yield from self._generator
        else:
            yield from  self._alerts


class WorkspaceModels:
    """Operates over the models of a concrete workspace.
    
    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.workspace.Workspace`.
    
    Attributes:
        workspace: the workspace with which to operate with its models.
    """

    def __init__(self, workspace: 'Workspace', models: List[Model]):
        self.workspace = workspace
        self._generator = None
        self._models = models

    def load(self):
        """Loads a workspace's models.

        If the models were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/models'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        response = handle_paginated_request(method='GET', path=path, headers=headers, credentials=self.workspace.credentials)

        # map results
        self._models = None
        self._generator = (
            Model.build(organization_id=self.workspace.organization_id, workspace_id=self.workspace.info.workspace_id, 
                        credentials=self.workspace.credentials, model_id=m['id']) for m in response)

    def create(self, name: str, description: str, model_type: ModelType, method: ModelMethod, source: Source,
               target_feature_name: str, configuration: dict = None, test_split_size: float = 0.3,
               shuffle_test_split: bool = False, initial_model_state: float = 0, hyper_parameters: dict = None,
               wait_for_model_creation: bool = True) -> Optional[Model]:
        """Creates an alert in current workspace.

        Before creation, the alert is loaded and stored locally in the internal list of alerts in the current instance.

        Args:
            name: model's name.
            description: model's description.
            model_type: type of model (classifier or regressor).
            method: method for prediction (bayes, logistic, forest, etc.).
            source: source used to train the model.
            target_feature_name: the feature that will be predicted. Within the :obj:`deepint.core.model.Model` is called output_feature.
            configuration: advanced model configuration.
            test_split_size: proportion of dataset to use for testing (between 0 and 1).
            shuffle_test_split: If set to True, it suffles the instances, else it follows the given order.
            initial_model_state: custom seed for rng method.
            hyper_parameters: Hyper-parametter search configfuration (Advanced).
            wait_for_model_creation: if set to True, before the model creation request, it waits for the model to be created (it can last several
                minutes).  In other case, only the model creation is requested, and then None is returned.

        Returns:
            the created model (if wait_for_model_creation is set to True) else None.
        """

        # check parameters
        configuration = configuration if configuration is not None else {}
        hyper_parameters = hyper_parameters if hyper_parameters is not None else {}

        allowed_methods = ModelMethod.allowed_methods_for_type(model_type)
        if method not in allowed_methods:
            raise DeepintBaseError(code='MODEL_MISMATCH',
                                   message=f'Provided model method ({method.name}) doesn\'t match for model type {model_type.name}. Allowed methods for provided type: {[x.name for x in allowed_methods]}')

        try:
            target_index = [f.index for f in source.features.fetch_all() if f.name == target_feature_name][0]
        except:
            raise DeepintBaseError(code='SOURCE_MISMATCH',
                                   message=f'Provided source for model creation was not found or provided target feature is not configured in the source.')

        # request
        path = f'/api/v1/workspace/{self.workspace.info.workspace_id}/models'
        headers = {'x-deepint-organization': self.workspace.organization_id}
        parameters = {
            'name': name,
            'description': description,
            'type': model_type.name,
            'method': method.name,
            'source': source.info.source_id,
            'target': target_index,
            'configuration': configuration,
            'training_configuration': {
                'test_size': test_split_size,
                'shuffle': shuffle_test_split,
                'random_state': initial_model_state
            },
            'hyper_search_configuration': hyper_parameters
        }
        response = handle_request(method='POST', path=path, headers=headers, credentials=self.workspace.credentials, parameters=parameters)

        # map response
        task = Task.build(task_id=response['task_id'], workspace_id=self.workspace.info.workspace_id,
                          organization_id=self.workspace.organization_id, credentials=self.workspace.credentials)

        if wait_for_model_creation:
            # wait for task to finish and build model
            task.resolve()
            task_result = task.fetch_result()
            new_model = Model.build(workspace_id=self.workspace.info.workspace_id, organization_id=self.workspace.organization_id, 
                                    credentials=self.workspace.credentials, model_id=task_result['model'])

            # update local state
            self._models = self._models if self._models is not None else []
            self._models.append(new_model)

            return new_model
        else:
            return None

    def fetch(self, model_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Model]:
        """Search for a model in the workspace.

        The first time is invoked, buidls a generator to retrieve models directly from deepint.net API. However, 
        if there is stored models and the force_reload option is not specified, only iterates in local 
        models. In other case, it request the models to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            model_id: model's id to search by.
            name: model's name to search by.
            force_reload: if set to True, models are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceModels.load` method.
        
        Returns:
            retrieved model if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if model_id is None and name is None:
            return None

        # search by given attributes
        if self._alerts is not None and not force_reload:
            for m in self._models:
                if m.info.model_id == model_id or m.info.name == name:
                    return m

        if self._generator is not None:
            for m in self._generator:
                if m.info.model_id == model_id or m.info.name == name:
                    return m

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Model, None, None]:
        """Retrieves all workspace's models.
        
        The first time is invoked, buidls a generator to retrieve models directly from deepint.net API. However, 
        if there is stored models and the force_reload option is not specified, only iterates in local 
        models. In other case, it request the models to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, models are reloaded before the search with the
                :obj:`deepint.core.workspace.WorkspaceModel.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Model`: The next model returned by deeepint.net API.

        Returns:
            the workspace's models.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._models is None:
            yield from self._generator
        else:
            yield from  self._models


class Workspace:
    """A Deep Intelligence workspace.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.workspace.Workspace.build`
    or :obj:`deepint.core.workspace.Workspace.from_url` methods. 
    
    Attributes:
        organization_id: the organziation where workspace is located.
        info: :obj:`deepint.core.workspace.WorkspaceInfo` to operate with workspace's information.
        tasks: :obj:`deepint.core.workspace.WorkspaceTasks` to operate with workspace's tasks.
        models: :obj:`deepint.core.workspace.WorkspaceModels` to operate with workspace's models.
        alerts: :obj:`deepint.core.workspace.WorkspaceAlerts` to operate with workspace's alerts.
        sources: :obj:`deepint.core.workspace.WorkspaceSources` to operate with workspace's sources.
        dashboards: :obj:`deepint.core.workspace.WorkspaceDashboards` to operate with workspace's dashboards.
        visualizations: :obj:`deepint.core.workspace.WorkspaceVisualizations` to operate with workspace's visualizations.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the workspace. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, credentials: Credentials, info: WorkspaceInfo, sources: List[Source], models: List[Model],
                 tasks: List[Task], alerts: List[Alert], visualizations: List[Visualization],
                 dashboards: List[Dashboard]) -> None:
        self.organization_id = organization_id
        self.info = info
        self.credentials = credentials
        self.tasks = WorkspaceTasks(self, tasks)
        self.models = WorkspaceModels(self, models)
        self.alerts = WorkspaceAlerts(self, alerts)
        self.sources = WorkspaceSources(self, sources)
        self.dashboards = WorkspaceDashboards(self, dashboards)
        self.visualizations = WorkspaceVisualizations(self, visualizations)

    def __str__(self):
        return f'<Workspace organization_id={self.organization_id} workspace={self.info.workspace_id} {self.info}>'

    def __eq__(self, other):
        if not isinstance(other, Workspace):
            return False
        else:
            return self.info == other.info

    @classmethod
    def build(cls, organization_id: str, workspace_id: str, credentials: Credentials = None) -> 'Workspace':
        """Builds a workspace.
        
        Note: when workspace is created, the workspace's information and list of it's associated objects (tasks, models, sources, etc.) are loaded.

        Args:
            organization_id: organization where workspace is located.
            workspace_id: workspace's id.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the workspace. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the workspace build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        info = WorkspaceInfo(workspace_id=workspace_id, name=None, description=None, created=None, last_modified=None,
                             last_access=None, sources_count=None, dashboards_count=None, visualizations_count=None,
                             models_count=None,
                             size_bytes=None)
        ws = cls(organization_id=organization_id, credentials=credentials, info=info, sources=None, models=None, 
                       tasks=None, alerts=None, visualizations=None, dashboards=None)
    
        ws.load()
        ws.tasks.load()
        ws.models.load()
        ws.alerts.load()
        ws.sources.load()
        ws.dashboards.load()
        ws.visualizations.load()

        return ws

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Workspace':
        """Builds a workspace from it's API or web associated URL.

        The url must contain the workspace's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42
        
        Note: when workspace is created, the workspace's information and list of it's associated objects (tasks, models, sources, etc.) are loaded.
            Also it is remmarkable that if the API URL is providen, the organization_id must be provided in the optional parameter, otherwise
            this ID won't be found on the URL and the Organization will not be created, raising a value error.

        Args:
            url: the workspace's API or web associated URL.
            organization_id: the id of the organziation. Must be providen if the API URL is used.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the workspace. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the workspace build with the URL and credentials.
        """

        url_info, hostname = parse_url(url)

        if 'organization_id' not in url_info and organization_id is None:
            raise ValueError('Fields organization_id must be in url to build the object. Or providen as optional parameter.')

        if 'workspace_id' not in url_info:
            raise ValueError('Fields workspace_id must be in url to build the object.')

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        new_credentials = Credentials(token=credentials.token, instance=hostname)
        
        return cls.build(organization_id=organization_id, workspace_id=url_info['workspace_id'], credentials=new_credentials)

    def load(self):
        """Loads the workspace's information.

        If the workspace's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/workspace/{self.info.workspace_id}'
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        self.info = WorkspaceInfo.from_dict(response)

    def update(self, name: str = None, description: str = None):
        """Updates a workspace's name and description.

        Args:
            name: workspace's name. If not provided the workspace's name stored in the :obj:`deepint.core.workspace.Workspace.workspace_info` attribute is taken.
            descrpition: workspace's description. If not provided the workspace's description stored in the :obj:`deepint.core.workspace.Workspace.workspace_info` attribute is taken.
        """

        # check parameters
        name = name if name is not None else self.info.name
        description = description if description is not None else self.info.description

        # request
        path = f'/api/v1/workspace/{self.info.workspace_id}'
        parameters = {'name': name, 'description': description}
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        # update local state
        self.info.name = name
        self.info.description = description

    def delete(self):
        """Deletes a workspace.
        """

        # request
        path = f'/api/v1/workspace/{self.info.workspace_id}'
        headers = {'x-deepint-organization': self.organization_id}
        handle_request(method='DELETE', path=path, headers=headers, credentials=self.credentials)

    def export(self, folder_path: str=".", wait_for_download: bool = True, task: Task = None) -> Union[str, Task]:
        """Exports a workspace to ZIP into the selected path.
        
        Args:
            folder_path: the path where the zip should be located. This parameter must contain the name of the file. By default is the
                current folder.
            wait_for_download: if set to true the file is located automatically into the selected path. In other case, the method
                returns a :obj:`deepint.core.task.Task`, that can be used later to get the ZIP with this metod, providing it into
                the task parameter.
            task: :obj:`deepint.core.task.Task` used to obtain the URL to download the ZIP in a delayed download (when the wait_for_download parameter is set to false).
        
        Returns:
            The path to downloaded ZIP in the case of wait_for_download is set to True. In other case the task generated to build the ZIP.
        """

        if task is None:

            # build request
            path = f'/api/v1/workspace/{self.info.workspace_id}/export'
            headers = {'x-deepint-organization': self.organization_id}
            response = handle_request(method='POST', path=path, headers=headers,credentials=self.credentials)

            # create task to fetch the ZIP file
            task = Task.build(task_id=response['task_id'], workspace_id=self.info.workspace_id,
                              organization_id=self.organization_id, credentials=self.credentials)

            if not wait_for_download:
                return task

        # wait for task resolution to obtain reslult
        task.resolve()
        result = task.fetch_result()

        if 'file' not in result:
            raise DeepintBaseError(code='DOWNLOAD_FAILED', message="The task generated to build the ZIP file failed, please try again in a few seconds")

        file_url = result['file']

        # download and store ZIP file
        try:            
            file_path = os.path.join(folder_path, f'{self.info.workspace_id}.zip')
            file_path = os.path.abspath(file_path)
            r = requests.get(file_url)
            open(file_path, 'wb').write(r.content)
            return file_path
        except:
            raise DeepintBaseError(code='DOWNLOAD_FAILED', message="Unable to write the file's content. Check the path and permisions.")

    def clone(self, name:str = None) -> 'Workspace':
        """Clones a workspace.
        
        Args:
            name: name for the new workspace. If not providen the name will be `Copy of <current workspace's name>`

        Returns:
            the cloned workspace instance.
        """

        # generate name fi not present
        if name is None:
            name = f'Copy of {self.info.name}'

        # request workspace clone
        path = f'/api/v1/workspace/{self.info.workspace_id}/clone'
        parameters = {'name': name}
        headers = {'x-deepint-organization': self.organization_id}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, credentials=self.credentials)

        # retrieve task
        task = Task.build(task_id=response['task_id'], workspace_id=response['workspace_id'], organization_id=self.organization_id, credentials=self.credentials)

        # resolve task and build workspace
        task.resolve()
        _ = task.fetch_result()

        new_workspace = Workspace.build(organization_id=self.organization_id, workspace_id=response['workspace_id'],
                                        credentials=self.credentials)
        return new_workspace
        

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"info": self.info.to_dict(), "tasks": [x.to_dict() for x in self.tasks.fetch_all()],
                "models": [x.to_dict() for x in self.models.fetch_all()],
                "alerts": [x.to_dict() for x in self.alerts.fetch_all()],
                "sources": [x.to_dict() for x in self.sources.fetch_all()],
                "dashboards": [x.to_dict() for x in self.dashboards.fetch_all()],
                "visualizations": [x.to_dict() for x in self.visualizations.fetch_all()]}
