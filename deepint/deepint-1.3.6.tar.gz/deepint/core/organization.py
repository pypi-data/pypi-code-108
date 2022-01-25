#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

from typing import Any, List, Dict, Optional, Generator

from ..auth import Credentials
from .workspace import Workspace
from .task import Task, TaskStatus
from ..error import DeepintBaseError
from ..util import handle_request, parse_date, parse_url


class OrganizationWorkspaces:
    """Operates over the worksapces of a concrete organization.

    Note: This class should not be instanced, and only be used within an :obj:`deepint.core.organization.Organization`
    
    Attributes:
        organization: the organization with which to operate with its worksapces
    """

    def __init__(self, organization: 'Organization', workspaces: List[Workspace]):
        self.organization = organization
        self._workspaces = workspaces
        self._generator = None

    def load(self):
        """Loads a organization's workspaces.

        If the workspaces were already loaded, this ones are replace by the new ones after retrieval.
        """

        # request
        path = f'/api/v1/workspaces'
        headers = {'x-deepint-organization': self.organization.organization_id}
        response = handle_request(method='GET', path=path, headers=headers, credentials=self.organization.credentials)

        # map results
        self._generator = (Workspace.build(organization_id=self.organization.organization_id, workspace_id=w['id'],
                           credentials=self.organization.credentials) for w in response)

    def create(self, name: str, description: str) -> Workspace:
        """Creates a workspace in current organization.

        Before creation, the workspace is loaded and stored locally in the internal list of workspaces in the current instance.

        Args:
            name: new workspace's name.
            descrpition: new workspace's description.
        
        Returns:
            the created workspace
        """

        # request
        path = f'/api/v1/workspaces/'
        headers = {'x-deepint-organization': self.organization.organization_id}
        parameters = {'name': name, 'description': description}
        response = handle_request(method='POST', path=path, credentials=self.organization.credentials,
                                  parameters=parameters, headers=headers)

        # map results
        new_workspace = Workspace.build(organization_id=self.organization.organization_id, workspace_id=response['workspace_id'],
                                        credentials=self.organization.credentials)

        # update local state
        self._workspaces = self._workspaces if self._workspaces is not None else []
        self._workspaces.append(new_workspace)

        return new_workspace

    def create_if_not_exists(self, name: str) -> Workspace:
        """Creates a workspace in current organization if not exists, else retrieves the given worksapce.

        The source is created with the :obj:`deepint.core.organization.OrganizationWorkspaces.create`, so it's reccomended to 
        read the documentation of that method to learn more about the possible artguments of creation.
        Before creation, the workspace is loaded and stored locally in the internal list of workspaces in the current instance.

        Args:
            name: new workspace's name.
        
        Returns:
            the created workspace if not exists, else the retrieved workspace
        """

        # retrieve selected workspace
        selected_workspace = self.fetch(name=name, force_reload=True)

        # if exists return
        if selected_workspace is not None:
            return selected_workspace

        # if not exists, create
        return self.create(name, '')

    def import_ws(self, name:str, description:str, file_path: str, wait_for_creation: bool = True) -> Workspace:
        """Imports a workspace to ZIP into the selected path.
        
        Args:
            name: new workspace's name.
            description: new workspace's description.
            file_path: the path where the zip must be located. This parameter must contain the name of the file.

        Returns:
            The created workspace in the case of wait_for_creation is set to True, or a task that on resolve will contain the
                workspace's id.
        """

        # read the file

        try:
            file_content = open(file_path,'rb').read()
        except:
            raise DeepintBaseError(code='FILE_NOT_FOUND', message=f'The providen ZIP file {path} was not found.')

        # build request
        path = f'/api/v1/workspaces/import'
        headers = {'x-deepint-organization': self.organization.organization_id}
        parameters = {'name': name, 'description': description}
        files = {'file': file_content}
        response = handle_request(method='POST', path=path, headers=headers, parameters=parameters, files=files, credentials=self.organization.credentials)

        # create task to fetch the workspace
        task = Task.build(task_id=response['task_id'], workspace_id=response['workspace_id'],
                          organization_id=self.organization.organization_id, credentials=self.organization.credentials)

        if not wait_for_creation:
            return task
        else:
            # wait for task resolution to obtain workspace
            task.resolve()
            _ = task.fetch_result()

            # map results
            new_workspace = Workspace.build(organization_id=self.organization.organization_id, workspace_id=response['workspace_id'],
                                            credentials=self.organization.credentials)

            # update local state
            self._workspaces = self._workspaces if self._workspaces is not None else []
            self._workspaces.append(new_workspace)

            return new_workspace

    def fetch(self, workspace_id: str = None, name: str = None, force_reload: bool = False) -> Optional[Workspace]:
        """Search for a workspace in the organization.

        The first time is invoked, buidls a generator to retrieve workspaces directly from deepint.net API. However, 
        if there is stored workspaces and the force_reload option is not specified, only iterates in local 
        workspaces. In other case, it request the workspaces to deepint.net API and iterates over it.

        Note: if no name or id is provided, the returned value is None.

        Args:
            workspace_id: workspace's id to search by.
            name: workspace's name to search by.
            force_reload: if set to True, workspaces are reloaded before the search with the
                :obj:`deepint.core.organization.OrganizationWorkspaces.load` method.
        
        Returns:
            retrieved workspace if found, and in other case None.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        # check parameters
        if workspace_id is None and name is None:
            return None

        # search by given attributes
        if self._workspaces is not None and not force_reload:
            for ws in self._workspaces:
                if ws.info.workspace_id == workspace_id or ws.info.name == name:
                    return ws

        if self._generator is not None:
            try:
                for ws in self._generator:
                    if ws.info.workspace_id == workspace_id or ws.info.name == name:
                        return ws
            except:
                # if there is an exception, a workspace does not exist anymore and needs to be reloaded
                self.load()
                for ws in self._generator:
                    if ws.info.workspace_id == workspace_id or ws.info.name == name:
                        return ws

        return None

    def fetch_all(self, force_reload: bool = False) -> Generator[Workspace, None, None]:
        """Retrieves all organization's workspaces.
        
        The first time is invoked, buidls a generator to retrieve workspaces directly from deepint.net API. However, 
        if there is stored workspaces and the force_reload option is not specified, only iterates in local 
        workspaces. In other case, it request the workspaces to deepint.net API and iterates over it.

        Args:
            force_reload: if set to True, workspaces are reloaded before the search with the
                :obj:`deepint.core.organization.OrganizationWorkspaces.load` method.
        
        Yields:
            :obj:`deepint.core.workspace.Workspace`: The next workspace returned by deeepint.net API.

        Returns:
            the organization's workspaces.
        """

        # if set to true reload
        if force_reload or self._generator is None:
            self.load()

        if force_reload or self._workspaces is None:
            yield from self._generator
        else:
            yield from self._workspaces



class Organization:
    """A Deep Intelligence Organization.
    
    Note: This class should not be instanced directly, and it's recommended to use the :obj:`deepint.core.organization.Organization.build`
        method.
    
    Attributes:
        organization_id: the id of the organization.
        workspaces: :obj:`deepint.core.organization.OrganizationWorkspaces` to operate with organization's workspaces.
        account: :obj:`dict` containing information about the providen token, like permissions and associated account details like id or name.
        credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the task. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.
    """

    def __init__(self, organization_id: str, credentials: Credentials, workspaces: List[Workspace], account: Dict[Any, Any]) -> None:
        self.account = account
        self.credentials = credentials
        self.organization_id = organization_id
        self.workspaces = OrganizationWorkspaces(self, workspaces)

    def __str__(self):
        return f'<Organization organization_id={self.organization_id} account={self.account}>'

    def __eq__(self, other):
        if not isinstance(other, Organization):
            return False
        else:
            return self.organization_id == other.organization_id
            
    @classmethod
    def build(cls, organization_id: str = None, credentials: Credentials = None) -> 'Organization':
        """Builds an organization.
        
        Note: when organization is created, the organization's information and account are retrieved from API.

        Args:
            organization_id: the id of the organization.
            credentials: credentials to authenticate with Deep Intelligence API and be allowed to perform operations over the organization. If
                 not provided, the credentials are generated with the :obj:`deepint.auth.credentials.Credentials.build`.

        Returns:
            the organization build with the given parameters and credentials.
        """

        credentials = credentials if credentials is not None else Credentials.build()
        org = cls(organization_id=organization_id, credentials=credentials, workspaces=None, account=None)
        org.load()
        org.workspaces.load()
        return org

    @classmethod
    def from_url(cls, url: str, organization_id: str = None, credentials: Credentials = None) -> 'Workspace':
        """Builds an organization from it's API or web associated URL.

        The url must contain the workspace's id as in the following examples:

        Example:
            - https://app.deepint.net/o/3a874c05-26d1-4b8c-894d-caf90e40078b/workspace?ws=f0e2095f-fe2b-479e-be4b-bbc77207f42d
            - https://app.deepint.net/api/v1/workspace/f0e2095f-fe2b-479e-be4b-bbc77207f42
        
        Note: when organization is created, the organization's information and list of it's associated objects (workspaces) are loaded. 
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

        organization_id = url_info['organization_id'] if 'organization_id' in url_info else organization_id

        # create new credentials
        new_credentials = Credentials(token=credentials.token, instance=hostname)
        
        return cls.build(organization_id=organization_id, credentials=new_credentials)

    def load(self):
        """Loads the organization's information and account.

        If the organization's or account's information is already loaded, is replace by the new one after retrieval.
        """

        # request
        path = f'/api/v1/who'
        headers = {'x-deepint-organization': self.organization_id}
        response_who = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        path = f'/api/v1/profile'
        headers = {'x-deepint-organization': self.organization_id}
        response_profile = handle_request(method='GET', path=path, headers=headers, credentials=self.credentials)

        # map results
        response = {**response_who, **response_profile}
        self.account = response

    def clean(self):
        """Deletes all workspaces in organization.
        """
        
        for ws in self.workspaces.fetch_all():
            ws.delete()
        self.workspaces.load()

    def to_dict(self) -> Dict[str, Any]:
        """Builds a dictionary containing the information stored in current object.

        Returns:
            dictionary contining the information stored in the current object.
        """

        return {"workspaces": [w.to_dict() for w in self.workspaces.fetch_all()]}
